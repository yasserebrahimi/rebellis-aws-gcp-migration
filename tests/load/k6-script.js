// k6 load script - API smoke & stress
import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  thresholds: {
    http_req_duration: ['p(95)<300'],
    http_req_failed: ['rate<0.01'],
  },
  scenarios: {
    smoke: { executor: 'constant-vus', vus: 5, duration: '1m' },
    stress: { executor: 'ramping-vus', startVUs: 10, stages: [
      { duration: '2m', target: 50 },
      { duration: '3m', target: 0 },
    ]}
  }
};

const BASE = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  let res = http.get(`${BASE}/health`);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(0.2);
}
