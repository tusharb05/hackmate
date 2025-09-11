data "aws_s3_bucket" "profile_photos" {
  bucket = "hackmate-profile-photos"
}

# Example: configure public access block for it
resource "aws_s3_bucket_public_access_block" "profile_photos_block" {
  bucket                  = data.aws_s3_bucket.profile_photos.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}