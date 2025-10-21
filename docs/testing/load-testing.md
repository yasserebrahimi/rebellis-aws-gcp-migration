# 📈 Load & Performance (k6)

Example scenario:
```js
import http from 'k6/http';
import { sleep } from 'k6';
export const options = { vus: 50, duration: '5m' };
export default function() {
  http.get('http://localhost:8000/health');
  sleep(1);
}
```
Gates: API p95 < 100 ms; error rate < 0.1%.
