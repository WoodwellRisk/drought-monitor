#!/usr/bin/env bash

# abort on errors, undefined vars, and pipe failures
set -euo pipefail

# https://github.com/google-github-actions/auth?tab=readme-ov-file#indirect-wif
# 1. Create a Google Cloud Service Account (already done)

# 2. Create a Workload Identity Pool
gcloud iam workload-identity-pools create ${POOL_ID} \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="${POOL_DISPLAY}"

# 3. Get the full ID of the Workload Identity Pool
gcloud iam workload-identity-pools describe "${POOL_ID}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)"

# 4. Create a Workload Identity Provider in that pool
gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_ID}" \
  --display-name="${PROVIDER_ID}" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner == '${GITHUB_ORG}' && assertion.repository == '${GITHUB_ORG}/${GITHUB_REPO}'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 5. Allow authentications from the Workload Identity Pool to your Google Cloud Service Account
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${PROVIDER}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"

# 6. Extract the Workload Identity Provider resource name
gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_ID}" \
  --format="value(name)"

# 7. Grant the Google Cloud Service Account permissions to access Google Cloud resources.
declare -a ROLES=(
  "roles/run.admin"
  "roles/run.invoker"
  "roles/run.viewer"
  "roles/cloudfunctions.admin"
  "roles/cloudfunctions.invoker"
  "roles/cloudbuild.builds.builder"
  "roles/cloudbuild.builds.editor"
  "roles/storage.objectAdmin"
  "roles/serviceusage.serviceUsageAdmin"
  "roles/serviceusage.serviceUsageConsumer"
  "roles/iam.serviceAccountUser"
)

echo "=== Granting operational roles to ${SA_EMAIL} ..."
for ROLE in "${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:${SA_EMAIL}" \
      --role="${ROLE}"
done

# allow the wif service account to impersonate the cloud build service account
gcloud iam service-accounts add-iam-policy-binding "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

# give new wif service account full control over the bucket
gsutil iam ch "serviceAccount:${SA_EMAIL}:objectAdmin" "gs://${BUCKET_NAME}"

# add more bucket-level permissions
gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.objectAdmin"

gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.legacyBucketReader"

# 8. Check wif attribute mappings
gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
    --project="$PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="$POOL_ID" \
    --format='json' | jq '.attributeMapping'

# 9. Verify new permissions
gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format='table(bindings.role, bindings.members)' \
    --filter="bindings.members:serviceAccount:${SA_EMAIL}"