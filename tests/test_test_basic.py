import pytest
import pickle
from troposphere import Template, Parameter, Ref, NoValue, If, Cidr, Sub, Split, Join, cloudformation, Region
from troposphere.ec2 import Instance
from troposphere.s3 import Bucket, PublicRead
from troposphere.ec2 import NetworkInterface, Route

"""
Pytest tests for troposphere functionalities to increase test coverage.
This file exercises various features such as resource instantiation, validation,
function output (Sub, Cidr, etc.), duplication-checks in Template, and pickling.
"""

def test_instance_unknown_property():
    """Test that creating an Instance with an unknown property raises AttributeError."""
    with pytest.raises(AttributeError):
        Instance("ec2instance", foobar=True)

def test_template_duplicate_resource():
    """Test that adding the same resource twice to a Template raises ValueError."""
    t = Template()
    b = Bucket("B1")
    t.add_resource(b)
    with pytest.raises(ValueError):
        t.add_resource(b)

def test_template_duplicate_parameter():
    """Test that adding the same parameter twice to a Template raises ValueError."""
    t = Template()
    p = Parameter("MyParameter", Type="String")
    t.add_parameter(p)
    with pytest.raises(ValueError):
        t.add_parameter(p)

def test_sub_function():
    """Test Sub function with mixed keyword arguments and dictionary.
    Here we pass the substitutions as kwargs and then validate the dict output.
    """
    # Passing variables via kwargs only
    s = "foo ${AWS::Region} ${sub1} ${sub2} ${sub3}"
    values = {"sub1": "una", "sub2": "dos", "sub3": "tres"}
    sub_obj = Sub(s, **values)
    out = sub_obj.to_dict()
    expected = {"Fn::Sub": [s, values]}
    assert out == expected

def test_ref_hash_consistency():
    """Test that the hash of a Ref object is consistent with the underlying value."""
    ref_obj = Ref("AWS::NoValue")
    hash_no_value = hash(NoValue)
    # Check that the Ref's hash equals that of the string "AWS::NoValue" and NoValue's hash.
    assert hash(ref_obj) == hash("AWS::NoValue") == hash_no_value

def test_route_no_validation():
    """Test that using .no_validation() on a Route resource bypasses validation errors."""
    route = Route(
        "Route66",
        DestinationCidrBlock="0.0.0.0/0",
        RouteTableId=Ref("RouteTable66"),
        InstanceId=If("UseNat", Ref("AWS::NoValue"), Ref("UseNat")),
        NatGatewayId=If("UseNat", Ref("UseNat"), Ref("AWS::NoValue")),
    ).no_validation()
    t = Template()
    t.add_resource(route)
    # This should complete without validation error.
    t.to_json()

def test_cidr_with_size_mask():
    """Test that Cidr returns the correct dictionary when a size mask argument is provided."""
    cidr = Cidr("10.1.10.1/24", 2, 10)
    expected = {"Fn::Cidr": ["10.1.10.1/24", 2, 10]}
    assert cidr.to_dict() == expected

def test_split_invalid_delimiter():
    """Test that calling Split with an invalid delimiter type raises ValueError."""
    with pytest.raises(ValueError):
        Split(10, "foobar")

def test_join_invalid_delimiter():
    """Test that calling Join with an invalid delimiter type raises ValueError."""
    with pytest.raises(ValueError):
        Join(10, "foobar")

def test_bucket_pickling():
    """Test that a Bucket object can be pickled and unpickled without losing attributes."""
    bucket = Bucket("B1", BucketName="testbucket")
    pkl = pickle.dumps(bucket)
    bucket2 = pickle.loads(pkl)
    assert bucket2.BucketName == bucket.BucketName
def test_cloudformation_wait_condition_handle_ref():
    """Test WaitConditionHandle returns proper Ref value."""
    from troposphere import cloudformation
    wch = cloudformation.WaitConditionHandle("TestResource")
    assert wch.Ref() == "TestResource"
def test_invalid_parameter_default_type():
    """Test that providing a default with an incorrect type for a Parameter raises a ValueError on validation."""
    from troposphere import Parameter
    with pytest.raises(ValueError):
        Parameter("TestParameter", Type="String", Default=123).validate()
def test_instance_pickling():
    """Test that an Instance can be pickled and unpickled correctly."""
    from troposphere.ec2 import Instance
    inst = Instance("MyInstance", ImageId="ami-123456")
    pkl = pickle.dumps(inst)
    inst2 = pickle.loads(pkl)
    assert inst2.ImageId == inst.ImageId
def test_empty_template_output():
    """Test that an empty Template produces valid JSON output."""
    from troposphere import Template
    t = Template()
    output = t.to_json()
    # ensure output is a non-empty string (i.e., valid JSON)
    assert isinstance(output, str) and len(output) > 0