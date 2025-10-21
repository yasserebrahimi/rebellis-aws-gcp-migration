#!/bin/bash
--namespace=${NAMESPACE} \
--dry-run=client -o yaml | kubectl apply -f -


helm upgrade --install ${PROJECT_NAME} \
./infrastructure/helm/rebellis \
--namespace=${NAMESPACE} \
--set image.tag=${VERSION} \
--set environment=${ENVIRONMENT} \
--values ./infrastructure/helm/rebellis/values.${ENVIRONMENT}.yaml \
--wait --timeout 10m


kubectl get pods -n ${NAMESPACE}
kubectl get svc -n ${NAMESPACE}
log_success "Kubernetes deployment complete"
}


post_deploy() {
log_info "Running post-deployment tasks..."


./scripts/health-check.sh || true


# Optional cache clear for production Redis (if running locally via compose)
if [[ "$ENVIRONMENT" == "production" ]] && command -v docker >/dev/null 2>&1; then
if docker compose ps redis >/dev/null 2>&1; then
docker compose exec -T redis redis-cli FLUSHDB || true
fi
fi


if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
curl -X POST -H 'Content-type: application/json' \
--data "{\"text\":\"✅ Deployed Rebellis ${VERSION} to ${ENVIRONMENT}\"}" \
${SLACK_WEBHOOK_URL}
fi


log_success "Post-deployment tasks complete"
}


rollback() {
log_error "Deployment failed! Rolling back..."
if [[ "$ENVIRONMENT" == "production" ]]; then
helm rollback ${PROJECT_NAME} --namespace=${NAMESPACE} || true
else
docker compose down || true
docker compose up -d || true
fi
}


main() {
trap rollback ERR


pre_deploy_checks
build_images
push_images


if [[ "$ENVIRONMENT" == "production" ]]; then
deploy_kubernetes
else
deploy_docker_compose
fi


post_deploy


echo ""
log_success "Deployment successful! 🚀"
echo ""
echo "Access points:"
echo " API: https://api-${ENVIRONMENT}.rebellis.ai (if configured)"
echo " Docs: https://api-${ENVIRONMENT}.rebellis.ai/docs"
echo " Monitoring: https://monitoring-${ENVIRONMENT}.rebellis.ai"
}


main