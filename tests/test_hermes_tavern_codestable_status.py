import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ATTENTION_DOC = REPO_ROOT / "design" / "codestable" / "attention.md"
CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-480 accepted"
STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-479 accepted"
STALE_PHASE_MARKER = "1-479"
STALE_PHASE_MARKER_EN_DASH = "1–479"
OLDER_STALE_PHASE_MARKER = "1-478"
OLDER_STALE_PHASE_MARKER_EN_DASH = "1–478"
REQUIRED_PHASE_LABELS = [
    "Phase 168 image settings JSON export",
    "Phase 169 project JSON export surface parity",
    "Phase 170 export command-surface regression",
    "Phase 171 root-design export parity",
    "Phase 172 attention status sync through Phase 171",
    "Phase 173 root-design section 17 import/export summary parity",
    "Phase 174 attention status sync through Phase 173",
    "Phase 175 attention status sync through Phase 174",
    "Phase 176 attention status sync through Phase 175",
    "Phase 177 attention status sync through Phase 176",
    "Phase 178 attention status sync through Phase 177",
    "Phase 179 attention status sync through Phase 178",
    "Phase 180 attention status sync through Phase 179",
    "Phase 181 attention status sync through Phase 180",
    "Phase 182 attention status sync through Phase 181",
    "Phase 183 attention status sync through Phase 182",
    "Phase 184 attention status sync through Phase 183",
    "Phase 185 attention status sync through Phase 184",
    "Phase 186 attention status sync through Phase 185",
    "Phase 187 attention status sync through Phase 186",
    "Phase 188 attention status sync through Phase 187",
    "Phase 189 attention status sync through Phase 188",
    "Phase 190 attention status sync through Phase 189",
    "Phase 191 attention status sync through Phase 190",
    "Phase 192 attention status sync through Phase 191",
    "Phase 193 attention status sync through Phase 192",
    "Phase 194 attention status sync through Phase 193",
    "Phase 195 attention status sync through Phase 194",
    "Phase 196 attention status sync through Phase 195",
    "Phase 197 attention status sync through Phase 196",
    "Phase 198 attention status sync through Phase 197",
    "Phase 199 attention status sync through Phase 198",
    "Phase 200 attention status sync through Phase 199",
    "Phase 201 attention status sync through Phase 200",
    "Phase 202 attention status sync through Phase 201",
    "Phase 203 attention status sync through Phase 202",
    "Phase 204 attention status sync through Phase 203",
    "Phase 205 attention status sync through Phase 204",
    "Phase 206 attention status sync through Phase 205",
    "Phase 207 attention status sync through Phase 206",
    "Phase 208 attention status sync through Phase 207",
    "Phase 209 attention status sync through Phase 208",
    "Phase 210 attention status sync through Phase 209",
    "Phase 211 attention status sync through Phase 210",
    "Phase 212 attention status sync through Phase 211",
    "Phase 213 attention status sync through Phase 212",
    "Phase 214 attention status sync through Phase 213",
    "Phase 215 attention status sync through Phase 214",
    "Phase 216 attention status sync through Phase 215",
    "Phase 217 attention status sync through Phase 216",
    "Phase 218 attention status sync through Phase 217",
    "Phase 219 attention status sync through Phase 218",
    "Phase 220 attention status sync through Phase 219",
    "Phase 221 attention status sync through Phase 220",
    "Phase 222 attention status sync through Phase 221",
    "Phase 223 attention status sync through Phase 222",
    "Phase 224 attention status sync through Phase 223",
    "Phase 225 attention status sync through Phase 224",
    "Phase 226 attention status sync through Phase 225",
    "Phase 227 attention status sync through Phase 226",
    "Phase 228 attention status sync through Phase 227",
    "Phase 229 attention status sync through Phase 228",
    "Phase 230 attention status sync through Phase 229",
    "Phase 231 attention status sync through Phase 230",
    "Phase 232 attention status sync through Phase 231",
    "Phase 233 attention status sync through Phase 232",
    "Phase 234 attention status sync through Phase 233",
    "Phase 235 attention status sync through Phase 234",
    "Phase 236 attention status sync through Phase 235",
    "Phase 237 attention status sync through Phase 236",
    "Phase 238 attention status sync through Phase 237",
    "Phase 239 attention status sync through Phase 238",
    "Phase 240 attention status sync through Phase 239",
    "Phase 241 attention status sync through Phase 240",
    "Phase 242 attention status sync through Phase 241",
    "Phase 243 attention status sync through Phase 242",
    "Phase 244 attention status sync through Phase 243",
    "Phase 245 attention status sync through Phase 244",
    "Phase 246 attention status sync through Phase 245",
    "Phase 247 attention status sync through Phase 246",
    "Phase 248 attention status sync through Phase 247",
    "Phase 249 attention status sync through Phase 248",
    "Phase 250 attention status sync through Phase 249",
    "Phase 251 attention status sync through Phase 250",
    "Phase 252 attention status sync through Phase 251",
    "Phase 253 attention status sync through Phase 252",
    "Phase 254 attention status sync through Phase 253",
    "Phase 255 attention status sync through Phase 254",
    "Phase 256 attention status sync through Phase 255",
    "Phase 257 attention status sync through Phase 256",
    "Phase 258 attention status sync through Phase 257",
    "Phase 259 attention status sync through Phase 258",
    "Phase 260 attention status sync through Phase 259",
    "Phase 261 attention status sync through Phase 260",
    "Phase 262 attention status sync through Phase 261",
    "Phase 263 attention status sync through Phase 262",
    "Phase 264 attention status sync through Phase 263",
    "Phase 265 attention status sync through Phase 264",
    "Phase 266 attention status sync through Phase 265",
    "Phase 267 attention status sync through Phase 266",
    "Phase 268 attention status sync through Phase 267",
    "Phase 269 attention status sync through Phase 268",
    "Phase 270 attention status sync through Phase 269",
    "Phase 271 attention status sync through Phase 270",
    "Phase 272 attention status sync through Phase 271",
    "Phase 273 attention status sync through Phase 272",
    "Phase 274 attention status sync through Phase 273",
    "Phase 275 attention status sync through Phase 274",
    "Phase 276 attention status sync through Phase 275",
    "Phase 277 attention status sync through Phase 276",
    "Phase 278 attention status sync through Phase 277",
    "Phase 279 attention status sync through Phase 278",
    "Phase 280 attention status sync through Phase 279",
    "Phase 281 attention status sync through Phase 280",
    "Phase 282 attention status sync through Phase 281",
    "Phase 283 attention status sync through Phase 282",
    "Phase 284 attention status sync through Phase 283",
    "Phase 285 attention status sync through Phase 284",
    "Phase 286 attention status sync through Phase 285",
    "Phase 287 attention status sync through Phase 286",
    "Phase 288 attention status sync through Phase 287",
    "Phase 289 attention status sync through Phase 288",
    "Phase 290 attention status sync through Phase 289",
    "Phase 291 attention status sync through Phase 290",
    "Phase 292 attention status sync through Phase 291",
    "Phase 293 attention status sync through Phase 292",
    "Phase 294 attention status sync through Phase 293",
    "Phase 295 attention status sync through Phase 294",
    "Phase 296 attention status sync through Phase 295",
    "Phase 297 attention status sync through Phase 296",
    "Phase 298 attention status sync through Phase 297",
    "Phase 299 attention status sync through Phase 298",
    "Phase 300 attention status sync through Phase 299",
    "Phase 301 attention status sync through Phase 300",
    "Phase 302 attention status sync through Phase 301",
    "Phase 303 attention status sync through Phase 302",
    "Phase 304 attention status sync through Phase 303",
    "Phase 305 attention status sync through Phase 304",
    "Phase 306 attention status sync through Phase 305",
    "Phase 307 attention status sync through Phase 306",
    "Phase 308 attention status sync through Phase 307",
    "Phase 309 attention status sync through Phase 308",
    "Phase 310 attention status sync through Phase 309",
    "Phase 311 attention status sync through Phase 310",
    "Phase 312 attention status sync through Phase 311",
    "Phase 313 attention status sync through Phase 312",
    "Phase 314 attention status sync through Phase 313",
    "Phase 315 attention status sync through Phase 314",
    "Phase 316 attention status sync through Phase 315",
    "Phase 317 attention status sync through Phase 316",
    "Phase 318 attention status sync through Phase 317",
    "Phase 319 attention status sync through Phase 318",
    "Phase 320 attention status sync through Phase 319",
    "Phase 321 attention status sync through Phase 320",
    "Phase 322 attention status sync through Phase 321",
    "Phase 323 attention status sync through Phase 322",
    "Phase 324 attention status sync through Phase 323",
    "Phase 325 attention status sync through Phase 324",
    "Phase 326 attention status sync through Phase 325",
    "Phase 327 attention status sync through Phase 326",
    "Phase 328 attention status sync through Phase 327",
    "Phase 329 attention status sync through Phase 328",
    "Phase 330 attention status sync through Phase 329",
    "Phase 331 attention status sync through Phase 330",
    "Phase 332 attention status sync through Phase 331",
    "Phase 333 attention status sync through Phase 332",
    "Phase 334 attention status sync through Phase 333",
    "Phase 335 attention status sync through Phase 334",
    "Phase 336 attention status sync through Phase 335",
    "Phase 337 attention status sync through Phase 336",
    "Phase 338 attention status sync through Phase 337",
    "Phase 339 attention status sync through Phase 338",
    "Phase 340 attention status sync through Phase 339",
    "Phase 341 attention status sync through Phase 340",
    "Phase 342 attention status sync through Phase 341",
    "Phase 343 attention status sync through Phase 342",
    "Phase 344 attention status sync through Phase 343",
    "Phase 345 attention status sync through Phase 344",
    "Phase 346 attention status sync through Phase 345",
    "Phase 347 attention status sync through Phase 346",
    "Phase 348 attention status sync through Phase 347",
    "Phase 349 attention status sync through Phase 348",
    "Phase 350 attention status sync through Phase 349",
    "Phase 351 attention status sync through Phase 350",
    "Phase 352 attention status sync through Phase 351",
    "Phase 353 attention status sync through Phase 352",
    "Phase 354 attention status sync through Phase 353",
    "Phase 355 attention status sync through Phase 354",
    "Phase 356 attention status sync through Phase 355",
    "Phase 357 attention status sync through Phase 356",
    "Phase 358 attention status sync through Phase 357",
    "Phase 359 attention status sync through Phase 358",
    "Phase 360 attention status sync through Phase 359",
    "Phase 361 attention status sync through Phase 360",
    "Phase 362 attention status sync through Phase 361",
    "Phase 363 attention status sync through Phase 362",
    "Phase 364 attention status sync through Phase 363",
    "Phase 365 attention status sync through Phase 364",
    "Phase 366 attention status sync through Phase 365",
    "Phase 367 attention status sync through Phase 366",
    "Phase 368 attention status sync through Phase 367",
    "Phase 369 attention status sync through Phase 368",
    "Phase 370 attention status sync through Phase 369",
    "Phase 371 attention status sync through Phase 370",
    "Phase 372 attention status sync through Phase 371",
    "Phase 373 attention status sync through Phase 372",
    "Phase 374 attention status sync through Phase 373",
    "Phase 375 attention status sync through Phase 374",
    "Phase 376 attention status sync through Phase 375",
    "Phase 377 attention status sync through Phase 376",
    "Phase 378 attention status sync through Phase 377",
    "Phase 379 attention status sync through Phase 378",
    "Phase 380 attention status sync through Phase 379",
    "Phase 381 attention status sync through Phase 380",
    "Phase 382 attention status sync through Phase 381",
    "Phase 383 attention status sync through Phase 382",
    "Phase 384 attention status sync through Phase 383",
    "Phase 385 attention status sync through Phase 384",
    "Phase 386 attention status sync through Phase 385",
    "Phase 387 attention status sync through Phase 386",
    "Phase 388 attention status sync through Phase 387",
    "Phase 389 attention status sync through Phase 388",
    "Phase 390 attention status sync through Phase 389",
    "Phase 391 attention status sync through Phase 390",
    "Phase 392 attention status sync through Phase 391",
    "Phase 393 attention status sync through Phase 392",
    "Phase 394 attention status sync through Phase 393",
    "Phase 395 attention status sync through Phase 394",
    "Phase 396 attention status sync through Phase 395",
    "Phase 397 attention status sync through Phase 396",
    "Phase 398 attention status sync through Phase 397",
    "Phase 399 attention status sync through Phase 398",
    "Phase 400 attention status sync through Phase 399",
    "Phase 401 attention status sync through Phase 400",
    "Phase 402 attention status sync through Phase 401",
    "Phase 403 attention status sync through Phase 402",
    "Phase 404 attention status sync through Phase 403",
    "Phase 405 attention status sync through Phase 404",
    "Phase 406 attention status sync through Phase 405",
    "Phase 407 attention status sync through Phase 406",
    "Phase 408 attention status sync through Phase 407",
    "Phase 409 attention status sync through Phase 408",
    "Phase 410 attention status sync through Phase 409",
    "Phase 411 attention status sync through Phase 410",
    "Phase 412 attention status sync through Phase 411",
    "Phase 413 attention status sync through Phase 412",
    "Phase 414 attention status sync through Phase 413",
    "Phase 415 attention status sync through Phase 414",
    "Phase 416 attention status sync through Phase 415",
    "Phase 417 attention status sync through Phase 416",
    "Phase 418 attention status sync through Phase 417",
    "Phase 419 attention status sync through Phase 418",
    "Phase 420 attention status sync through Phase 419",
    "Phase 421 attention status sync through Phase 420",
    "Phase 422 attention status sync through Phase 421",
    "Phase 423 attention status sync through Phase 422",
    "Phase 424 attention status sync through Phase 423",
    "Phase 425 attention status sync through Phase 424",
    "Phase 426 attention status sync through Phase 425",
    "Phase 427 attention status sync through Phase 426",
    "Phase 428 attention status sync through Phase 427",
    "Phase 429 attention status sync through Phase 428",
    "Phase 430 attention status sync through Phase 429",
    "Phase 431 attention status sync through Phase 430",
    "Phase 432 attention status sync through Phase 431",
    "Phase 433 attention status sync through Phase 432",
    "Phase 434 attention status sync through Phase 433",
    "Phase 435 attention status sync through Phase 434",
    "Phase 436 attention status sync through Phase 435",
    "Phase 437 attention status sync through Phase 436",
    "Phase 438 attention status sync through Phase 437",
    "Phase 439 attention status sync through Phase 438",
    "Phase 440 attention status sync through Phase 439",
    "Phase 441 attention status sync through Phase 440",
    "Phase 442 attention status sync through Phase 441",
    "Phase 443 attention status sync through Phase 442",
    "Phase 444 attention status sync through Phase 443",
    "Phase 445 attention status sync through Phase 444",
    "Phase 446 attention status sync through Phase 445",
    "Phase 447 attention status sync through Phase 446",
    "Phase 448 attention status sync through Phase 447",
    "Phase 449 attention status sync through Phase 448",
    "Phase 450 attention status sync through Phase 449",
    "Phase 451 attention status sync through Phase 450",
    "Phase 452 attention status sync through Phase 451",
    "Phase 453 attention status sync through Phase 452",
    "Phase 454 attention status sync through Phase 453",
    "Phase 455 attention status sync through Phase 454",
    "Phase 456 attention status sync through Phase 455",
    "Phase 457 attention status sync through Phase 456",
    "Phase 458 attention status sync through Phase 457",
    "Phase 459 attention status sync through Phase 458",
    "Phase 460 attention status sync through Phase 459",
    "Phase 461 attention status sync through Phase 460",
    "Phase 462 attention status sync through Phase 461",
    "Phase 463 attention status sync through Phase 462",
    "Phase 464 attention status sync through Phase 463",
    "Phase 465 attention status sync through Phase 464",
    "Phase 466 attention status sync through Phase 465",
    "Phase 467 attention status sync through Phase 466",
    "Phase 468 attention status sync through Phase 467",
    "Phase 469 attention status sync through Phase 468",
    "Phase 470 attention status sync through Phase 469",
    "Phase 471 attention status sync through Phase 470",
    "Phase 472 attention status sync through Phase 471",
    "Phase 473 attention status sync through Phase 472",
    "Phase 474 attention status sync through Phase 473",
    "Phase 475 attention status sync through Phase 474",
    "Phase 476 attention status sync through Phase 475",
    "Phase 477 attention status sync through Phase 476",
    "Phase 478 attention status sync through Phase 477",
    "Phase 479 attention status sync through Phase 478",
    "Phase 480 attention status sync through Phase 479",
]
FINAL_STATUS_SUFFIX = "Phase 478 attention status sync through Phase 477, Phase 479 attention status sync through Phase 478, and Phase 480 attention status sync through Phase 479."


def test_attention_current_status_line_is_current():
    lines = ATTENTION_DOC.read_text(encoding="utf-8").splitlines()

    status_lines = [line for line in lines if re.match(r"^\s*-\s*Current status ", line)]

    assert len(status_lines) == 1
    status = status_lines[0]
    other_header = "### 其他"
    adult_boundary = "- Adult-fiction non-negotiable boundaries defined in design doc §12.3 — do not build features that bypass provider safety systems."
    credentials_header = "### Hermes Tavern 凭证约束"
    status_index = lines.index(status)

    assert other_header in lines
    assert adult_boundary in lines
    assert credentials_header in lines
    assert lines.index(other_header) < lines.index(adult_boundary) < status_index
    assert status_index == lines.index(adult_boundary) + 1
    assert status_index < lines.index(credentials_header)

    assert status.startswith(f"- {CURRENT_STATUS_PREFIX}")
    for label in REQUIRED_PHASE_LABELS:
        assert label in status
    assert STALE_STATUS_PREFIX not in status
    assert re.search(rf"(?<!\d){re.escape(STALE_PHASE_MARKER)}(?!\d)", status) is None
    assert re.search(rf"(?<!\d){re.escape(STALE_PHASE_MARKER_EN_DASH)}(?!\d)", status) is None
    assert re.search(rf"(?<!\d){re.escape(OLDER_STALE_PHASE_MARKER)}(?!\d)", status) is None
    assert re.search(rf"(?<!\d){re.escape(OLDER_STALE_PHASE_MARKER_EN_DASH)}(?!\d)", status) is None
    assert status.endswith(FINAL_STATUS_SUFFIX)
    phase_range = range(168, 481)
    aggregate_range = "range(168, 481)"
    assert all(f"Phase {phase} " in status for phase in phase_range)
    assert re.search(r"(?<!\d)Phase 121-167(?!\d)", status) is not None
    test = Path(__file__).read_text(encoding="utf-8")
    assert aggregate_range in test
    assert re.findall(r"^CURRENT_STATUS_PREFIX\s*=", test, re.M) == ["CURRENT_STATUS_PREFIX ="]
    assert re.findall(r"^FINAL_STATUS_SUFFIX\s*=", test, re.M) == ["FINAL_STATUS_SUFFIX ="]
    assert CURRENT_STATUS_PREFIX in test
    assert all(label in test for label in REQUIRED_PHASE_LABELS)
    stale_aggregate_range_351 = "".join(["range(168, ", "35", "1", ")"])
    stale_aggregate_range_352 = "".join(["range(168, ", "35", "2", ")"])
    stale_aggregate_range_353 = "".join(["range(168, ", "35", "3", ")"])
    stale_aggregate_range_354 = "".join(["range(168, ", "35", "4", ")"])
    stale_aggregate_range_355 = "".join(["range(168, ", "35", "5", ")"])
    stale_aggregate_range_356 = "".join(["range(168, ", "35", "6", ")"])
    stale_aggregate_range_357 = "".join(["range(168, ", "35", "7", ")"])
    stale_aggregate_range_358 = "".join(["range(168, ", "35", "8", ")"])
    stale_aggregate_range_359 = "".join(["range(168, ", "35", "9", ")"])
    stale_aggregate_range_360 = "".join(["range(168, ", "36", "0", ")"])
    stale_aggregate_range_361 = "".join(["range(168, ", "36", "1", ")"])
    stale_aggregate_range_366 = "".join(["range(168, ", "36", "6", ")"])
    stale_aggregate_range_367 = "".join(["range(168, ", "36", "7", ")"])
    stale_aggregate_range_369 = "".join(["range(168, ", "36", "9", ")"])
    stale_aggregate_range_370 = "".join(["range(168, ", "37", "0", ")"])
    stale_aggregate_range_371 = "".join(["range(168, ", "37", "1", ")"])
    stale_aggregate_range_372 = "".join(["range(168, ", "37", "2", ")"])
    stale_aggregate_range_373 = "".join(["range(168, ", "37", "3", ")"])
    stale_aggregate_range_374 = "".join(["range(168, ", "37", "4", ")"])
    stale_aggregate_range_375 = "".join(["range(168, ", "37", "5", ")"])
    stale_aggregate_range_368 = "".join(["range(168, ", "36", "8", ")"])
    stale_aggregate_range_365 = "".join(["range(168, ", "36", "5", ")"])
    stale_aggregate_range_364 = "".join(["range(168, ", "36", "4", ")"])
    stale_aggregate_range_363 = "".join(["range(168, ", "36", "3", ")"])
    stale_aggregate_range_362 = "".join(["range(168, ", "36", "2", ")"])
    stale_aggregate_range_376 = "".join(["range(168, ", "37", "6", ")"])
    stale_aggregate_range_377 = "".join(["range(168, ", "37", "7", ")"])
    stale_aggregate_range_378 = "".join(["range(168, ", "37", "8", ")"])
    stale_aggregate_range_379 = "".join(["range(168, ", "37", "9", ")"])
    stale_aggregate_range_380 = "".join(["range(168, ", "38", "0", ")"])
    stale_aggregate_range_381 = "".join(["range(168, ", "38", "1", ")"])
    stale_aggregate_range_382 = "".join(["range(168, ", "38", "2", ")"])
    stale_aggregate_range_383 = "".join(["range(168, ", "38", "3", ")"])
    stale_aggregate_range_384 = "".join(["range(168, ", "38", "4", ")"])
    stale_aggregate_range_385 = "".join(["range(168, ", "38", "5", ")"])
    stale_aggregate_range_386 = "".join(["range(168, ", "38", "6", ")"])
    stale_aggregate_range_387 = "".join(["range(168, ", "38", "7", ")"])
    stale_aggregate_range_388 = "".join(["range(168, ", "38", "8", ")"])
    stale_aggregate_range_389 = "".join(["range(168, ", "38", "9", ")"])
    stale_aggregate_range_390 = "".join(["range(168, ", "39", "0", ")"])
    stale_aggregate_range_391 = "".join(["range(168, ", "39", "1", ")"])
    stale_aggregate_range_392 = "".join(["range(168, ", "39", "2", ")"])
    stale_aggregate_range_393 = "".join(["range(168, ", "39", "3", ")"])
    stale_aggregate_range_394 = "".join(["range(168, ", "39", "4", ")"])
    stale_aggregate_range_395 = "".join(["range(168, ", "39", "5", ")"])
    stale_aggregate_range_396 = "".join(["range(168, ", "39", "6", ")"])
    stale_aggregate_range_397 = "".join(["range(168, ", "39", "7", ")"])
    stale_aggregate_range_398 = "".join(["range(168, ", "39", "8", ")"])
    stale_aggregate_range_399 = "".join(["range(168, ", "39", "9", ")"])
    stale_aggregate_range_400 = "".join(["range(168, ", "40", "0", ")"])
    stale_aggregate_range_401 = "".join(["range(168, ", "40", "1", ")"])
    stale_aggregate_range_402 = "".join(["range(168, ", "40", "2", ")"])
    stale_aggregate_range_403 = "".join(["range(168, ", "40", "3", ")"])
    stale_aggregate_range_404 = "".join(["range(168, ", "40", "4", ")"])
    stale_aggregate_range_405 = "".join(["range(168, ", "40", "5", ")"])
    stale_aggregate_range_406 = "".join(["range(168, ", "40", "6", ")"])
    stale_aggregate_range_407 = "".join(["range(168, ", "40", "7", ")"])
    stale_aggregate_range_408 = "".join(["range(168, ", "40", "8", ")"])
    stale_aggregate_range_409 = "".join(["range(168, ", "40", "9", ")"])
    stale_aggregate_range_410 = "".join(["range(168, ", "41", "0", ")"])
    stale_aggregate_range_411 = "".join(["range(168, ", "41", "1", ")"])
    stale_aggregate_range_412 = "".join(["range(168, ", "41", "2", ")"])
    stale_aggregate_range_413 = "".join(["range(168, ", "41", "3", ")"])
    stale_aggregate_range_414 = "".join(["range(168, ", "41", "4", ")"])
    stale_aggregate_range_415 = "".join(["range(168, ", "41", "5", ")"])
    stale_aggregate_range_416 = "".join(["range(168, ", "41", "6", ")"])
    stale_aggregate_range_417 = "".join(["range(168, ", "41", "7", ")"])
    stale_aggregate_range_418 = "".join(["range(168, ", "41", "8", ")"])
    stale_aggregate_range_419 = "".join(["range(168, ", "41", "9", ")"])
    stale_aggregate_range_420 = "".join(["range(168, ", "42", "0", ")"])
    stale_aggregate_range_421 = "".join(["range(168, ", "42", "1", ")"])
    stale_aggregate_range_422 = "".join(["range(168, ", "42", "2", ")"])
    stale_aggregate_range_423 = "".join(["range(168, ", "42", "3", ")"])
    stale_aggregate_range_424 = "".join(["range(168, ", "42", "4", ")"])
    stale_aggregate_range_425 = "".join(["range(168, ", "42", "5", ")"])
    stale_aggregate_range_426 = "".join(["range(168, ", "42", "6", ")"])
    stale_aggregate_range_427 = "".join(["range(168, ", "42", "7", ")"])
    stale_aggregate_range_428 = "".join(["range(168, ", "42", "8", ")"])
    stale_aggregate_range_429 = "".join(["range(168, ", "42", "9", ")"])
    stale_aggregate_range_430 = "".join(["range(168, ", "43", "0", ")"])
    stale_aggregate_range_431 = "".join(["range(168, ", "43", "1", ")"])
    stale_aggregate_range_432 = "".join(["range(168, ", "43", "2", ")"])
    stale_aggregate_range_433 = "".join(["range(168, ", "43", "3", ")"])
    stale_aggregate_range_434 = "".join(["range(168, ", "43", "4", ")"])
    stale_aggregate_range_435 = "".join(["range(168, ", "43", "5", ")"])
    stale_aggregate_range_436 = "".join(["range(168, ", "43", "6", ")"])
    stale_aggregate_range_437 = "".join(["range(168, ", "43", "7", ")"])
    stale_aggregate_range_438 = "".join(["range(168, ", "43", "8", ")"])
    stale_aggregate_range_439 = "".join(["range(168, ", "43", "9", ")"])
    stale_aggregate_range_440 = "".join(["range(168, ", "44", "0", ")"])
    stale_aggregate_range_441 = "".join(["range(168, ", "44", "1", ")"])
    stale_aggregate_range_442 = "".join(["range(168, ", "44", "2", ")"])
    stale_aggregate_range_443 = "".join(["range(168, ", "44", "3", ")"])
    stale_aggregate_range_444 = "".join(["range(168, ", "44", "4", ")"])
    stale_aggregate_range_445 = "".join(["range(168, ", "44", "5", ")"])
    stale_aggregate_range_446 = "".join(["range(168, ", "44", "6", ")"])
    stale_aggregate_range_447 = "".join(["range(168, ", "44", "7", ")"])
    stale_aggregate_range_448 = "".join(["range(168, ", "44", "8", ")"])
    stale_aggregate_range_449 = "".join(["range(168, ", "44", "9", ")"])
    stale_aggregate_range_450 = "".join(["range(168, ", "45", "0", ")"])
    stale_aggregate_range_451 = "".join(["range(168, ", "45", "1", ")"])
    stale_aggregate_range_452 = "".join(["range(168, ", "45", "2", ")"])
    stale_aggregate_range_453 = "".join(["range(168, ", "45", "3", ")"])
    stale_aggregate_range_454 = "".join(["range(168, ", "45", "4", ")"])
    stale_aggregate_range_455 = "".join(["range(168, ", "45", "5", ")"])
    stale_aggregate_range_456 = "".join(["range(168, ", "45", "6", ")"])
    stale_aggregate_range_457 = "".join(["range(168, ", "45", "7", ")"])
    stale_aggregate_range_458 = "".join(["range(168, ", "45", "8", ")"])
    stale_aggregate_range_459 = "".join(["range(168, ", "45", "9", ")"])
    stale_aggregate_range_460 = "".join(["range(168, ", "46", "0", ")"])
    stale_aggregate_range_461 = "".join(["range(168, ", "46", "1", ")"])
    stale_aggregate_range_462 = "".join(["range(168, ", "46", "2", ")"])
    stale_aggregate_range_463 = "".join(["range(168, ", "46", "3", ")"])
    stale_aggregate_range_464 = "".join(["range(168, ", "46", "4", ")"])
    stale_aggregate_range_465 = "".join(["range(168, ", "46", "5", ")"])
    stale_aggregate_range_466 = "".join(["range(168, ", "46", "6", ")"])
    stale_aggregate_range_467 = "".join(["range(168, ", "46", "7", ")"])
    stale_aggregate_range_468 = "".join(["range(168, ", "46", "8", ")"])
    stale_aggregate_range_469 = "".join(["range(168, ", "46", "9", ")"])
    stale_aggregate_range_470 = "".join(["range(168, ", "47", "0", ")"])
    stale_aggregate_range_471 = "".join(["range(168, ", "47", "1", ")"])
    stale_aggregate_range_472 = "".join(["range(168, ", "47", "2", ")"])
    stale_aggregate_range_473 = "".join(["range(168, ", "47", "3", ")"])
    stale_aggregate_range_474 = "".join(["range(168, ", "47", "4", ")"])
    stale_aggregate_range_475 = "".join(["range(168, ", "47", "5", ")"])
    stale_aggregate_range_476 = "".join(["range(168, ", "47", "6", ")"])
    stale_aggregate_range_477 = "".join(["range(168, ", "47", "7", ")"])
    stale_aggregate_range_478 = "".join(["range(168, ", "47", "8", ")"])
    stale_aggregate_range_479 = "".join(["range(168, ", "47", "9", ")"])
    stale_aggregate_range_480 = "".join(["range(168, ", "48", "0", ")"])
    stale_aggregate_range_349 = "".join(["range(168, ", "34", "9", ")"])
    stale_aggregate_range_350 = "".join(["range(168, ", "35", "0", ")"])
    stale_aggregate_range_348 = "".join(["range(168, ", "34", "8", ")"])
    stale_aggregate_range_347 = "".join(["range(168, ", "34", "7", ")"])
    stale_aggregate_range_341 = "".join(["range(168, ", "34", "1", ")"])
    stale_aggregate_range_342 = "".join(["range(168, ", "34", "2", ")"])
    stale_aggregate_range_343 = "".join(["range(168, ", "34", "3", ")"])
    stale_aggregate_range_344 = "".join(["range(168, ", "34", "4", ")"])
    stale_aggregate_range_345 = "".join(["range(168, ", "34", "5", ")"])
    stale_aggregate_range_346 = "".join(["range(168, ", "34", "6", ")"])
    stale_aggregate_range_340 = "".join(["range(168, ", "34", "0", ")"])
    stale_aggregate_range_339 = "".join(["range(168, ", "33", "9", ")"])
    stale_aggregate_range_338 = "".join(["range(168, ", "33", "8", ")"])
    stale_aggregate_range_329 = "".join(["range(168, ", "32", "9", ")"])
    stale_aggregate_range_330 = "".join(["range(168, ", "33", "0", ")"])
    stale_aggregate_range_331 = "".join(["range(168, ", "33", "1", ")"])
    stale_aggregate_range_332 = "".join(["range(168, ", "33", "2", ")"])
    stale_aggregate_range_333 = "".join(["range(168, ", "33", "3", ")"])
    stale_aggregate_range_334 = "".join(["range(168, ", "33", "4", ")"])
    stale_aggregate_range_335 = "".join(["range(168, ", "33", "5", ")"])
    stale_aggregate_range_336 = "".join(["range(168, ", "33", "6", ")"])
    stale_aggregate_range_337 = "".join(["range(168, ", "33", "7", ")"])
    stale_aggregate_range_327 = "".join(["range(168, ", "32", "7", ")"])
    stale_aggregate_range_328 = "".join(["range(168, ", "32", "8", ")"])
    stale_aggregate_range_326 = "".join(["range(168, ", "32", "6", ")"])
    stale_aggregate_range_324 = "".join(["range(168, ", "32", "4", ")"])
    stale_aggregate_range_325 = "".join(["range(168, ", "32", "5", ")"])
    stale_aggregate_range_322 = "".join(["range(168, ", "32", "2", ")"])
    stale_aggregate_range_323 = "".join(["range(168, ", "32", "3", ")"])
    stale_aggregate_range_311 = "".join(["range(168, ", "31", "1", ")"])
    stale_aggregate_range_313 = "".join(["range(168, ", "31", "3", ")"])
    stale_aggregate_range_321 = "".join(["range(168, ", "32", "1", ")"])
    stale_aggregate_range_320 = "".join(["range(168, ", "32", "0", ")"])
    stale_aggregate_range_318 = "".join(["range(168, ", "31", "8", ")"])
    stale_aggregate_range_319 = "".join(["range(168, ", "31", "9", ")"])
    stale_aggregate_range_317 = "".join(["range(168, ", "31", "7", ")"])
    stale_aggregate_range_316 = "".join(["range(168, ", "31", "6", ")"])
    stale_aggregate_range_315 = "".join(["range(168, ", "31", "5", ")"])
    stale_aggregate_range_314 = "".join(["range(168, ", "31", "4", ")"])
    stale_aggregate_range_312 = "".join(["range(168, ", "31", "2", ")"])
    stale_aggregate_range_310 = "".join(["range(168, ", "31", "0", ")"])
    stale_aggregate_range_309 = "".join(["range(168, ", "30", "9", ")"])
    stale_aggregate_range_308 = "".join(["range(168, ", "30", "8", ")"])
    stale_aggregate_range_306 = "".join(["range(168, ", "30", "6", ")"])
    stale_aggregate_range_307 = "".join(["range(168, ", "30", "7", ")"])
    stale_aggregate_range_305 = "".join(["range(168, ", "30", "5", ")"])
    stale_aggregate_range_303 = "".join(["range(168, ", "30", "3", ")"])
    stale_aggregate_range_302 = "".join(["range(168, ", "30", "2", ")"])
    stale_aggregate_range_300 = "".join(["range(168, ", "30", "0", ")"])
    stale_aggregate_range_301 = "".join(["range(168, ", "30", "1", ")"])
    stale_aggregate_range_304 = "".join(["range(168, ", "30", "4", ")"])
    stale_aggregate_range_297 = "".join(["range(168, ", "29", "7", ")"])
    stale_aggregate_range_299 = "".join(["range(168, ", "29", "9", ")"])
    stale_aggregate_range_298 = "".join(["range(168, ", "29", "8", ")"])
    stale_aggregate_range_296 = "".join(["range(168, ", "29", "6", ")"])
    stale_aggregate_range_295 = "".join(["range(168, ", "29", "5", ")"])
    stale_aggregate_range_294 = "".join(["range(168, ", "29", "4", ")"])
    stale_aggregate_range_293 = "".join(["range(168, ", "29", "3", ")"])
    stale_aggregate_range_292 = "".join(["range(168, ", "29", "2", ")"])
    stale_aggregate_range_291 = "".join(["range(168, ", "29", "1", ")"])
    stale_aggregate_range_290 = "".join(["range(168, ", "29", "0", ")"])
    stale_aggregate_range_289 = "".join(["range(168, ", "28", "9", ")"])
    stale_aggregate_range_288 = "".join(["range(168, ", "28", "8", ")"])
    stale_aggregate_range_287 = "".join(["range(168, ", "28", "7", ")"])
    stale_aggregate_range_286 = "".join(["range(168, ", "28", "6", ")"])
    stale_aggregate_range_285 = "".join(["range(168, ", "28", "5", ")"])
    stale_aggregate_range_284 = "".join(["range(168, ", "28", "4", ")"])
    stale_aggregate_range_283 = "".join(["range(168, ", "28", "3", ")"])
    stale_aggregate_range_282 = "".join(["range(168, ", "28", "2", ")"])
    stale_aggregate_range_281 = "".join(["range(168, ", "28", "1", ")"])
    for stale_range in (
        stale_aggregate_range_372,
        stale_aggregate_range_367,
        stale_aggregate_range_368,
        stale_aggregate_range_369,
        stale_aggregate_range_370,
        stale_aggregate_range_371,
        stale_aggregate_range_366,
        stale_aggregate_range_365,
        stale_aggregate_range_364,
        stale_aggregate_range_363,
        stale_aggregate_range_355,
        stale_aggregate_range_356,
        stale_aggregate_range_357,
        stale_aggregate_range_360,
        stale_aggregate_range_361,
        stale_aggregate_range_362,
        stale_aggregate_range_359,
        stale_aggregate_range_358,
        stale_aggregate_range_374,
        stale_aggregate_range_353,
        stale_aggregate_range_351,
        stale_aggregate_range_352,
        stale_aggregate_range_350,
        stale_aggregate_range_349,
        stale_aggregate_range_348,
        stale_aggregate_range_347,
        stale_aggregate_range_341,
        stale_aggregate_range_340,
        stale_aggregate_range_339,
        stale_aggregate_range_337,
        stale_aggregate_range_346,
        stale_aggregate_range_345,
        stale_aggregate_range_343,
        stale_aggregate_range_344,
        stale_aggregate_range_342,
        stale_aggregate_range_338,
        stale_aggregate_range_333,
        stale_aggregate_range_336,
        stale_aggregate_range_335,
        stale_aggregate_range_354,
        stale_aggregate_range_334,
        stale_aggregate_range_331,
        stale_aggregate_range_329,
        stale_aggregate_range_330,
        stale_aggregate_range_328,
        stale_aggregate_range_327,
        stale_aggregate_range_326,
        stale_aggregate_range_324,
        stale_aggregate_range_325,
        stale_aggregate_range_323,
        stale_aggregate_range_322,
        stale_aggregate_range_321,
        stale_aggregate_range_320,
        stale_aggregate_range_318,
        stale_aggregate_range_317,
        stale_aggregate_range_319,
        stale_aggregate_range_316,
        stale_aggregate_range_315,
        stale_aggregate_range_314,
        stale_aggregate_range_313,
        stale_aggregate_range_312,
        stale_aggregate_range_311,
        stale_aggregate_range_310,
        stale_aggregate_range_309,
        stale_aggregate_range_308,
        stale_aggregate_range_307,
        stale_aggregate_range_306,
        stale_aggregate_range_305,
        stale_aggregate_range_304,
        stale_aggregate_range_303,
        stale_aggregate_range_302,
        stale_aggregate_range_301,
        stale_aggregate_range_300,
        stale_aggregate_range_299,
        stale_aggregate_range_298,
        stale_aggregate_range_297,
        stale_aggregate_range_296,
        stale_aggregate_range_295,
        stale_aggregate_range_294,
        stale_aggregate_range_293,
        stale_aggregate_range_292,
        stale_aggregate_range_291,
        stale_aggregate_range_290,
        stale_aggregate_range_289,
        stale_aggregate_range_288,
        stale_aggregate_range_287,
        stale_aggregate_range_286,
        stale_aggregate_range_285,
        stale_aggregate_range_284,
        stale_aggregate_range_283,
        stale_aggregate_range_282,
        stale_aggregate_range_281,
        stale_aggregate_range_375,
        stale_aggregate_range_373,
        stale_aggregate_range_377,
        stale_aggregate_range_378,
        stale_aggregate_range_379,
        stale_aggregate_range_380,
        stale_aggregate_range_381,
        stale_aggregate_range_382,
        stale_aggregate_range_383,
        stale_aggregate_range_384,
        stale_aggregate_range_385,
        stale_aggregate_range_386,
        stale_aggregate_range_387,
        stale_aggregate_range_388,
        stale_aggregate_range_389,
        stale_aggregate_range_390,
        stale_aggregate_range_391,
        stale_aggregate_range_392,
        stale_aggregate_range_393,
        stale_aggregate_range_394,
        stale_aggregate_range_395,
        stale_aggregate_range_396,
        stale_aggregate_range_397,
        stale_aggregate_range_398,
        stale_aggregate_range_399,
        stale_aggregate_range_400,
        stale_aggregate_range_401,
        stale_aggregate_range_402,
        stale_aggregate_range_403,
        stale_aggregate_range_404,
        stale_aggregate_range_405,
        stale_aggregate_range_406,
        stale_aggregate_range_407,
        stale_aggregate_range_408,
        stale_aggregate_range_409,
        stale_aggregate_range_410,
        stale_aggregate_range_411,
        stale_aggregate_range_412,
        stale_aggregate_range_413,
        stale_aggregate_range_414,
        stale_aggregate_range_415,
        stale_aggregate_range_416,
        stale_aggregate_range_417,
        stale_aggregate_range_418,
        stale_aggregate_range_419,
        stale_aggregate_range_420,
        stale_aggregate_range_421,
        stale_aggregate_range_422,
        stale_aggregate_range_423,
        stale_aggregate_range_424,
        stale_aggregate_range_425,
        stale_aggregate_range_426,
        stale_aggregate_range_427,
        stale_aggregate_range_428,
        stale_aggregate_range_429,
        stale_aggregate_range_430,
        stale_aggregate_range_431,
        stale_aggregate_range_432,
        stale_aggregate_range_433,
        stale_aggregate_range_434,
        stale_aggregate_range_435,
        stale_aggregate_range_436,
        stale_aggregate_range_437,
        stale_aggregate_range_438,
        stale_aggregate_range_439,
        stale_aggregate_range_440,
        stale_aggregate_range_441,
        stale_aggregate_range_442,
        stale_aggregate_range_443,
        stale_aggregate_range_444,
        stale_aggregate_range_445,
        stale_aggregate_range_446,
        stale_aggregate_range_447,
        stale_aggregate_range_448,
        stale_aggregate_range_449,
        stale_aggregate_range_450,
        stale_aggregate_range_451,
        stale_aggregate_range_452,
        stale_aggregate_range_453,
        stale_aggregate_range_454,
        stale_aggregate_range_455,
        stale_aggregate_range_456,
        stale_aggregate_range_457,
        stale_aggregate_range_458,
        stale_aggregate_range_459,
        stale_aggregate_range_460,
        stale_aggregate_range_462,
        stale_aggregate_range_461,
        stale_aggregate_range_463,
        stale_aggregate_range_464,
        stale_aggregate_range_465,
        stale_aggregate_range_466,
        stale_aggregate_range_467,
        stale_aggregate_range_468,
        stale_aggregate_range_469,
        stale_aggregate_range_470,
        stale_aggregate_range_471,
        stale_aggregate_range_472,
        stale_aggregate_range_473,
        stale_aggregate_range_475,
        stale_aggregate_range_476,
        stale_aggregate_range_477,
        stale_aggregate_range_478,
        stale_aggregate_range_479,
        stale_aggregate_range_480,
        stale_aggregate_range_474,
        stale_aggregate_range_376,
    ):
        assert stale_range not in test
    stale_aggregate_guard_480 = "".join(["range(168, ", "48", str(0), ")"])
    stale_aggregate_guard_470 = "".join(["range(168, ", "47", str(0), ")"])
    stale_aggregate_guard_471 = "".join(["range(168, ", "47", str(1), ")"])
    stale_aggregate_guard_472 = "".join(["range(168, ", "47", str(2), ")"])
    stale_aggregate_guard_473 = "".join(["range(168, ", "47", str(3), ")"])
    stale_aggregate_guard_474 = "".join(["range(168, ", "47", str(4), ")"])
    stale_aggregate_guard_475 = "".join(["range(168, ", "47", str(5), ")"])
    stale_aggregate_guard_476 = "".join(["range(168, ", "47", str(6), ")"])
    stale_aggregate_guard_477 = "".join(["range(168, ", "47", str(7), ")"])
    stale_aggregate_guard_478 = "".join(["range(168, ", "47", str(8), ")"])
    stale_aggregate_guard_479 = "".join(["range(168, ", "47", str(9), ")"])
    stale_aggregate_guard_469 = "".join(["range(168, ", "46", str(9), ")"])
    stale_aggregate_guard_468 = "".join(["range(168, ", "46", str(8), ")"])
    stale_aggregate_guard_467 = "".join(["range(168, ", "46", str(7), ")"])
    stale_aggregate_guard_466 = "".join(["range(168, ", "46", str(6), ")"])
    stale_aggregate_guard_465 = "".join(["range(168, ", "46", str(5), ")"])
    stale_aggregate_guard_464 = "".join(["range(168, ", "46", str(4), ")"])
    stale_aggregate_guard_463 = "".join(["range(168, ", "46", str(3), ")"])
    stale_aggregate_guard_462 = "".join(["range(168, ", "46", str(2), ")"])
    stale_aggregate_guard_461 = "".join(["range(168, ", "46", str(1), ")"])
    stale_aggregate_guard_460 = "".join(["range(168, ", "46", str(0), ")"])
    stale_aggregate_guard_459 = "".join(["range(168, ", "45", str(9), ")"])
    stale_aggregate_guard_458 = "".join(["range(168, ", "45", str(8), ")"])
    stale_aggregate_guard_457 = "".join(["range(168, ", "45", str(7), ")"])
    stale_aggregate_guard_456 = "".join(["range(168, ", "45", str(6), ")"])
    stale_aggregate_guard_455 = "".join(["range(168, ", "45", str(5), ")"])
    stale_aggregate_guard_454 = "".join(["range(168, ", "45", str(4), ")"])
    stale_aggregate_guard_453 = "".join(["range(168, ", "45", str(3), ")"])
    stale_aggregate_guard_452 = "".join(["range(168, ", "45", str(2), ")"])
    stale_aggregate_guard_451 = "".join(["range(168, ", "45", str(1), ")"])
    stale_aggregate_guard_450 = "".join(["range(168, ", "45", str(0), ")"])
    stale_aggregate_guard_449 = "".join(["range(168, ", "44", str(9), ")"])
    stale_aggregate_guard_448 = "".join(["range(168, ", "44", str(8), ")"])
    stale_aggregate_guard_447 = "".join(["range(168, ", "44", str(7), ")"])
    stale_aggregate_guard_446 = "".join(["range(168, ", "44", str(6), ")"])
    stale_aggregate_guard_445 = "".join(["range(168, ", "44", str(5), ")"])
    stale_aggregate_guard_444 = "".join(["range(168, ", "44", str(4), ")"])
    stale_aggregate_guard_443 = "".join(["range(168, ", "44", str(3), ")"])
    stale_aggregate_guard_442 = "".join(["range(168, ", "44", str(2), ")"])
    stale_aggregate_guard_441 = "".join(["range(168, ", "44", str(1), ")"])
    stale_aggregate_guard_440 = "".join(["range(168, ", "44", str(0), ")"])
    stale_aggregate_guard_439 = "".join(["range(168, ", "43", str(9), ")"])
    stale_aggregate_guard_438 = "".join(["range(168, ", "43", str(8), ")"])
    stale_aggregate_guard_437 = "".join(["range(168, ", "43", str(7), ")"])
    stale_aggregate_guard_436 = "".join(["range(168, ", "43", str(6), ")"])
    stale_aggregate_guard_435 = "".join(["range(168, ", "43", str(5), ")"])
    stale_aggregate_guard_434 = "".join(["range(168, ", "43", str(4), ")"])
    stale_aggregate_guard_433 = "".join(["range(168, ", "43", str(3), ")"])
    stale_aggregate_guard_432 = "".join(["range(168, ", "43", str(2), ")"])
    stale_aggregate_guard_431 = "".join(["range(168, ", "43", str(1), ")"])
    stale_aggregate_guard_430 = "".join(["range(168, ", "43", str(0), ")"])
    stale_aggregate_guard_429 = "".join(["range(168, ", "42", str(9), ")"])
    stale_aggregate_guard_428 = "".join(["range(168, ", "42", str(8), ")"])
    stale_aggregate_guard_426 = "".join(["range(168, ", "42", str(6), ")"])
    stale_aggregate_guard_427 = "".join(["range(168, ", "42", str(7), ")"])
    stale_aggregate_guard_425 = "".join(["range(168, ", "42", str(5), ")"])
    stale_aggregate_guard_421 = "".join(["range(168, ", "42", str(1), ")"])
    stale_aggregate_guard_422 = "".join(["range(168, ", "42", str(2), ")"])
    stale_aggregate_guard_423 = "".join(["range(168, ", "42", str(3), ")"])
    stale_aggregate_guard_424 = "".join(["range(168, ", "42", str(4), ")"])
    assert stale_aggregate_guard_480 not in test
    assert stale_aggregate_guard_479 not in test
    assert stale_aggregate_guard_478 not in test
    assert stale_aggregate_guard_477 not in test
    assert stale_aggregate_guard_476 not in test
    assert stale_aggregate_guard_475 not in test
    assert stale_aggregate_guard_474 not in test
    assert stale_aggregate_guard_473 not in test
    assert stale_aggregate_guard_472 not in test
    assert stale_aggregate_guard_471 not in test
    assert stale_aggregate_guard_470 not in test
    assert stale_aggregate_guard_469 not in test
    assert stale_aggregate_guard_468 not in test
    assert stale_aggregate_guard_467 not in test
    assert stale_aggregate_guard_466 not in test
    assert stale_aggregate_guard_465 not in test
    assert stale_aggregate_guard_464 not in test
    assert stale_aggregate_guard_463 not in test
    assert stale_aggregate_guard_462 not in test
    assert stale_aggregate_guard_461 not in test
    assert stale_aggregate_guard_460 not in test
    assert stale_aggregate_guard_459 not in test
    assert stale_aggregate_guard_458 not in test
    assert stale_aggregate_guard_457 not in test
    assert stale_aggregate_guard_456 not in test
    assert stale_aggregate_guard_455 not in test
    assert stale_aggregate_guard_454 not in test
    assert stale_aggregate_guard_453 not in test
    assert stale_aggregate_guard_452 not in test
    assert stale_aggregate_guard_451 not in test
    assert stale_aggregate_guard_450 not in test
    assert stale_aggregate_guard_449 not in test
    assert stale_aggregate_guard_448 not in test
    assert stale_aggregate_guard_447 not in test
    assert stale_aggregate_guard_446 not in test
    assert stale_aggregate_guard_445 not in test
    assert stale_aggregate_guard_444 not in test
    assert stale_aggregate_guard_443 not in test
    assert stale_aggregate_guard_442 not in test
    assert stale_aggregate_guard_441 not in test
    assert stale_aggregate_guard_440 not in test
    assert stale_aggregate_guard_439 not in test
    assert stale_aggregate_guard_438 not in test
    assert stale_aggregate_guard_437 not in test
    assert stale_aggregate_guard_436 not in test
    assert stale_aggregate_guard_435 not in test
    assert stale_aggregate_guard_434 not in test
    assert stale_aggregate_guard_433 not in test
    assert stale_aggregate_guard_432 not in test
    assert stale_aggregate_guard_431 not in test
    assert stale_aggregate_guard_430 not in test
    assert stale_aggregate_guard_429 not in test
    assert stale_aggregate_guard_428 not in test
    assert stale_aggregate_guard_426 not in test
    assert stale_aggregate_guard_427 not in test
    assert stale_aggregate_guard_425 not in test
    assert stale_aggregate_guard_421 not in test
    assert stale_aggregate_guard_422 not in test
    assert stale_aggregate_guard_423 not in test
    assert stale_aggregate_guard_424 not in test
    forbidden_glob = "." + "glob" + "("
    forbidden_rglob = "." + "rgl" + "ob" + "("
    assert forbidden_glob not in test
    assert forbidden_rglob not in test
    forbidden_iterdir = "iter" + "dir("
    forbidden_os_walk = "os" + "." + "walk"
    assert forbidden_iterdir not in test
    assert forbidden_os_walk not in test
