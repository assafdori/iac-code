resource "aws_vpc" "resume-app-vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "resume-app-vpc"
  }
}
