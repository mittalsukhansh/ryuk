CREATE INDEX checkout_capture_ref ON checkouts(json_extract(body,'$.capture_id'));
CREATE INDEX checkout_order_ref ON checkouts(json_extract(body,'$.order_id'));
