KV='nats -s nats://a:a@localhost:4222 kv'
BUCKET='JL-pricing_state'
$KV rm -f $BUCKET
$KV add $BUCKET
$KV put $BUCKET subscriptions '[]'
