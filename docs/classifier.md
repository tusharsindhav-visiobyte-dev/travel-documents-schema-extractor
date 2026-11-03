# How the classifier works

`POST /document-type` turns pasted text, or the text of an uploaded file, into one document type from the schema registry. It does not extract fields, validate a payload, or create travel events. The response is only:

```json
{"document_type": "flight_ticket"}
```

The identifier is one of the registered schema names, such as `flight_ticket`, `hotel_voucher`, or `passport`. Event names such as `flight_departure` are not document types and cannot be returned.

## Where the allowed answers come from

Every specialized schema is registered with a fixed `document_type` and a `SCHEMA_CATEGORY`. `get_supported_document_types_by_category()` reads that registry. The classifier caches the result and uses it for both model calls.

Current categories are `activities`, `bus`, `corporate`, `cruise`, `financial`, `flight`, `hotel`, `identity`, `insurance`, `itinerary`, `road`, `special`, `train`, and `transfers`. A newly registered schema appears in the prompts on the next process start because the list is built from the registry, not copied into the classifier.

## Path from request to answer

```text
request
  -> plain text
  -> category call
  -> document-type call inside that category
  -> registry check
  -> {"document_type": "..."}
```

`api/app.py` accepts the request. `api/extract.py` reads an upload. `api/classifier.py` calls the model twice. `registry.validate_document_type()` checks the final identifier before it is returned.

### 1. The request becomes text

Three inputs are accepted:

| Content type | What is classified |
| --- | --- |
| `application/json` | The `text` string. |
| `application/x-www-form-urlencoded` | The `text` field. |
| `multipart/form-data` | The `file` when it has bytes. Otherwise the `text` field. |

A text upload is decoded as UTF-8. Recognized text files include `.txt`, `.md`, `.csv`, `.json`, `.html`, and `.xml`. A PDF is detected by its extension, media type, or `%PDF` header. `pypdf` reads the first 20 pages and joins the extracted text. A scanned PDF with no text layer is rejected.

Images are rejected. The endpoint does not run OCR.

Limits, from `api/config.py`:

- An upload larger than 15 MB is rejected.
- Text longer than 12,000 characters is cut at that point before either model call. The kept portion is the start of the document, where the title and reference numbers usually are.

Empty text is rejected before the model is called.

### 2. The model picks a category

The first call sends the whole document and one line per category. Each line lists that category's registered identifiers:

```text
- flight: flight_ticket, flight_booking_confirmation, flight_boarding_pass, ...
- identity: passport, visa, evisa, ...
```

The prompt also states two distinctions that the model otherwise confuses: an airline ticket, PNR, coupon, or boarding pass is `flight`; a passport, visa, or residence permit is `identity`.

Ollama is asked for JSON whose only field is `category`. The JSON schema enum is exactly the category names from the registry, and `temperature` is 0. The model cannot freely invent a label such as "electronic ticket" at this step; the grammar only allows a registered category.

### 3. The model picks one document type

The second call sees only the types in the chosen category, each with the description stored on its schema. For `flight`, that includes the difference between an issued ticket, a booking confirmation, and a boarding pass.

Example line:

```text
- flight_ticket: An issued flight ticket or e-ticket. Ticket numbers and coupons distinguish it from a booking confirmation.
```

This call's JSON schema enum contains only those identifiers. A hotel type is not offered after the category call returned `flight`.

### 4. The answer is checked again

The reply is parsed as JSON. A surrounding Markdown fence is stripped if the model adds one. The value is trimmed, lowercased, and turned into a registry-style identifier: spaces and hyphens become underscores, so `Flight Ticket` becomes `flight_ticket`.

The value must be one of the identifiers allowed for that call. The final document type must also pass `validate_document_type()`. Anything else becomes HTTP 422 and is not returned as a document type.

## Model settings

`api/config.py` reads the project `.env` without overriding variables that are already set in the process.

| Setting | `.env` name | Default |
| --- | --- | --- |
| Ollama base URL | `ollama_url` or `OLLAMA_URL` | `http://localhost:11435` |
| Model name | `LLM_MODEL` | `qwen:7b` |

Each call is `POST {ollama_url}/api/chat` with streaming off and a 120 second timeout. One classification is two of those calls.

## HTTP results

| Status | Meaning |
| --- | --- |
| 200 | `document_type` is a registered schema identifier. |
| 400 | The body was missing, empty, or the file had no readable text. |
| 415 | The upload was not a text file or a PDF. |
| 422 | The model answer was not one of the allowed registry identifiers. |
| 502 | Ollama could not be reached, returned an error, or returned a body that was not JSON. |

## What this step leaves untouched

The classifier chooses the schema. It does not fill that schema. Field extraction, `validate_document`, business rules, and travel events stay separate. A returned `flight_ticket` means the text was classified as that document, not that a `FlightTicketSchema` payload was built.
