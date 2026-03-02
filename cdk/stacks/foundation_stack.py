from aws_cdk import (
    Stack,
    CfnParameter,
    CfnTag,
    aws_ec2 as ec2,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class FoundationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Parameters – mirror the original template
        environment_name = CfnParameter(
            self,
            "EnvironmentName",
            type="String",
            description="An environment name that is prefixed to resource names",
        )

        vpc_cidr = CfnParameter(
            self,
            "VpcCIDR",
            type="String",
            description="Please enter the IP range (CIDR notation) for this VPC",
            default="10.192.0.0/16",
        )

        public_subnet1_cidr = CfnParameter(
            self,
            "PublicSubnet1CIDR",
            type="String",
            description="Please enter the IP range (CIDR notation) for the public subnet in the first Availability Zone",
            default="10.192.10.0/24",
        )

        public_subnet2_cidr = CfnParameter(
            self,
            "PublicSubnet2CIDR",
            type="String",
            description="Please enter the IP range (CIDR notation) for the public subnet in the second Availability Zone",
            default="10.192.11.0/24",
        )

        s3_bucket_name = CfnParameter(
            self,
            "S3BucketForCourse",
            type="String",
            description="Please enter the name for your S3 bucket. This will used throughout the course and must be unique globally within AWS.",
        )

        # VPC
        vpc = ec2.Vpc(
            self,
            "VPC",
            cidr=vpc_cidr.value_as_string,
            enable_dns_support=True,
            enable_dns_hostnames=True,
            max_azs=2,  # We'll use first two AZs
            subnet_configuration=[],  # We'll define subnets manually to match exact CIDRs
        )

        # Override default subnets – create exactly two public ones with specified CIDRs
        subnet1 = ec2.PublicSubnet(
            self,
            "PublicSubnet1",
            vpc_id=vpc.vpc_id,
            availability_zone=ec2.Vpc.SELECT_AZ_0,  # First AZ
            cidr_block=public_subnet1_cidr.value_as_string,
            map_public_ip_on_launch=True,
        )
        subnet1.node.add_dependency(vpc)

        subnet2 = ec2.PublicSubnet(
            self,
            "PublicSubnet2",
            vpc_id=vpc.vpc_id,
            availability_zone=ec2.Vpc.SELECT_AZ_1,  # Second AZ
            cidr_block=public_subnet2_cidr.value_as_string,
            map_public_ip_on_launch=True,
        )
        subnet2.node.add_dependency(vpc)

        # Internet Gateway + Attachment
        igw = ec2.CfnInternetGateway(
            self,
            "InternetGateway",
        )
        vpc_gw_attachment = ec2.CfnVPCGatewayAttachment(
            self,
            "InternetGatewayAttachment",
            vpc_id=vpc.vpc_id,
            internet_gateway_id=igw.ref,
        )

        # Public Route Table
        public_route_table = ec2.CfnRouteTable(
            self,
            "PublicRouteTable",
            vpc_id=vpc.vpc_id,
        )

        # Default route to IGW
        default_route = ec2.CfnRoute(
            self,
            "DefaultPublicRoute",
            route_table_id=public_route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=igw.ref,
        )
        default_route.node.add_dependency(vpc_gw_attachment)

        # Route table associations
        ec2.CfnSubnetRouteTableAssociation(
            self,
            "PublicSubnet1RouteTableAssociation",
            subnet_id=subnet1.subnet_id,
            route_table_id=public_route_table.ref,
        )

        ec2.CfnSubnetRouteTableAssociation(
            self,
            "PublicSubnet2RouteTableAssociation",
            subnet_id=subnet2.subnet_id,
            route_table_id=public_route_table.ref,
        )

        # S3 Bucket
        s3_bucket = s3.Bucket(
            self,
            "S3BucketFordataEngineeringCourse",
            bucket_name=s3_bucket_name.value_as_string,
            removal_policy=RemovalPolicy.RETAIN,  # Safer default; change to DESTROY for dev if desired
            versioned=False,  # Original doesn't have versioning
        )

        # Tags – apply consistently (CDK tags are easier on resources)
        common_tags = [
            CfnTag(key="Name", value=environment_name.value_as_string),
            CfnTag(key="course", value="dataEngineeringCourse"),
        ]

        # Apply tags via low-level (since high-level may not propagate everywhere)
        for resource in [vpc, igw, subnet1, subnet2, public_route_table, s3_bucket.node.default_child]:
            if hasattr(resource, "tags"):
                for tag in common_tags:
                    resource.tags.set_tag(tag.key, tag.value)

        # Outputs
        CfnOutput(self, "VPC", value=vpc.vpc_id, description="A reference to the created VPC")
        CfnOutput(
            self,
            "PublicSubnets",
            value=f"{subnet1.subnet_id},{subnet2.subnet_id}",
            description="A list of the public subnets",
        )
        CfnOutput(self, "PublicSubnet1", value=subnet1.subnet_id, description="Public subnet in AZ1")
        CfnOutput(self, "PublicSubnet2", value=subnet2.subnet_id, description="Public subnet in AZ2")
        CfnOutput(self, "S3BucketName", value=s3_bucket.bucket_name)