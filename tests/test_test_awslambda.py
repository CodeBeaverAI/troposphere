import pytest
from troposphere import GetAtt, Join, Ref, Template
from troposphere.awslambda import Code, Environment, Function, ImageConfig, validate_memory_size
from troposphere.validators.awslambda import check_zip_file

# Pytest tests to increase coverage for AWS Lambda resource definitions

def test_validate_image_uri_with_zipfile():
    """Test that Code validation fails when both ImageUri and ZipFile are provided."""
    with pytest.raises(ValueError):
        Code(ImageUri="something", ZipFile="something").validate()

def test_validate_s3_missing_required_keys():
    """Test that Code validation fails for S3 properties missing required keys."""
    with pytest.raises(ValueError):
        Code(S3Bucket="bucket", S3ObjectVersion="version").validate()  # Missing S3Key
    with pytest.raises(ValueError):
        Code(S3Key="key", S3ObjectVersion="version").validate()  # Missing S3Bucket

def test_validate_s3_success():
    """Test that Code validation succeeds with proper S3 parameters."""
    # Valid S3 parameters: Both S3Bucket and S3Key are provided.
    Code(S3Bucket="bucket", S3Key="key").validate()

def test_function_package_type_invalid():
    """Test that Function validation raises error for invalid PackageType."""
    with pytest.raises(ValueError):
        Function("TestFunction", Code=Code(ImageUri="something"), PackageType="Invalid", Role=GetAtt("LambdaExecutionRole", "Arn")).validate()

def test_image_config_command_length():
    """Test that ImageConfig validation raises error if Command list is too long."""
    with pytest.raises(ValueError):
        ImageConfig(Command=["a"] * 1501).validate()

def test_image_config_entrypoint_length():
    """Test that ImageConfig validation raises error if EntryPoint list is too long."""
    with pytest.raises(ValueError):
        ImageConfig(EntryPoint=["a"] * 1501).validate()

def test_image_config_working_directory_length():
    """Test that ImageConfig validation raises error if WorkingDirectory is too long."""
    with pytest.raises(ValueError):
        ImageConfig(WorkingDirectory="x" * 1001).validate()

def test_function_with_zip_code():
    """Test creation and validation of a Function with ZipFile code block."""
    lambda_func = Function(
        "AMIIDLookup",
        Handler="index.handler",
        Role=GetAtt("LambdaExecutionRole", "Arn"),
        Code=Code(ZipFile=Join("", ["exports.handler = function(event, context) { console.log(event); };"])),
        Runtime="nodejs",
        PackageType="Zip"
    )
    lambda_func.validate()

def test_environment_variable_invalid_names():
    """Test that Environment validation rejects invalid variable names."""
    invalid_names = ["1", "2var", "_var", "/var"]
    for var in invalid_names:
        with pytest.raises(ValueError):
            Environment(Variables={var: "value"})

def test_environment_variable_reserved_names():
    """Test that Environment validation rejects reserved variable names."""
    reserved = ["AWS_ACCESS_KEY", "AWS_ACCESS_KEY_ID", "AWS_LAMBDA_FUNCTION_MEMORY_SIZE"]
    for var in reserved:
        with pytest.raises(ValueError):
            Environment(Variables={var: "value"})

def test_check_zip_file_positive_and_negative():
    """Test check_zip_file with both valid and invalid inputs."""
    positive_tests = [
        "a" * 4096,
        Join("", ["a" * 4096]),
        Join("", ["a", 10]),
        Join("", ["a" * 4096, Ref("EmptyParameter")]),
        Join("ab", ["a" * 2047, "a" * 2047]),
        GetAtt("foo", "bar"),
    ]
    for z in positive_tests:
        check_zip_file(z)

    negative_tests = [
        "a" * 4097,
        Join("", ["a" * 4097]),
        Join("", ["a" * 4097, Ref("EmptyParameter")]),
        Join("abc", ["a" * 2047, "a" * 2047]),
    ]
    for z in negative_tests:
        with pytest.raises(ValueError):
            check_zip_file(z)

def test_validate_memory_size_boundaries():
    """Test that validate_memory_size accepts valid memory sizes."""
    valid_sizes = ["128", "129", "10240"]
    for size in valid_sizes:
        validate_memory_size(size)

def test_validate_memory_size_invalid():
    """Test that validate_memory_size rejects invalid memory sizes."""
    invalid_sizes = ["1", "111111111111111111111"]
    for size in invalid_sizes:
        with pytest.raises(ValueError) as excinfo:
            validate_memory_size(size)
        assert str(excinfo.value) == "Lambda Function memory size must be between 128 and 10240"
def test_image_config_boundary_valid():
    """Test that ImageConfig with Command, EntryPoint, and WorkingDirectory exactly on the allowed boundaries passes validation."""
    command = ["a"] * 1500
    entrypoint = ["b"] * 1500
    working_directory = "x" * 1000
    ic = ImageConfig(Command=command, EntryPoint=entrypoint, WorkingDirectory=working_directory)
    # This should not raise any error
    ic.validate()

def test_code_empty():
    """Test that an empty Code definition (with no properties) fails validation."""
    with pytest.raises(ValueError):
        Code().validate()

def test_environment_variables_edge_valid():
    """Test that Environment accepts edge-case valid variable names that meet the regex requirements."""
    # Using names that start with a letter and have at least one additional character, with only letters, digits, or underscores.
    valid_names = ["Ab", "a_b", "ENV1"]
    for name in valid_names:
        Environment(Variables={name: "value"})
def test_code_s3_with_intrinsic():
    """
    Test that Code with S3 properties using an intrinsic function (Ref) in S3Bucket passes validation.
    """
    # Ref is already imported from troposphere in the file so we use it directly
    Code(S3Bucket=Ref("MyBucket"), S3Key="key", S3ObjectVersion="version").validate()

def test_validate_memory_size_non_numeric():
    """
    Test that validate_memory_size raises a ValueError when passed a non-numeric string.
    """
    with pytest.raises(ValueError):
            validate_memory_size("abc")
# End of tests
def test_package_type_image_with_zip_file():
    """Test that Function with PackageType 'Image' and using a ZipFile does not raise an error.
    (The current implementation does not enforce an error for a ZipFile with PackageType Image.)"""
    Function(
        "TestFunction",
        Code=Code(ZipFile="exports.handler = lambda event: None"),
        PackageType="Image",
        Role=GetAtt("LambdaExecutionRole", "Arn")
    ).validate()

def test_function_zip_missing_handler():
    """Test that Function with PackageType 'Zip' missing Handler property does not raise an error.
    (The current implementation does not enforce a required Handler for ZIP packages.)"""
    # Calling validate() should not raise an exception even if Handler is missing.
    Function(
        "TestFunction",
        Code=Code(ZipFile="exports.handler = lambda event: None"),
        PackageType="Zip",
        Role=GetAtt("LambdaExecutionRole", "Arn"),
        Runtime="nodejs"
    ).validate()

def test_function_zip_missing_runtime():
    """Test that Function with PackageType 'Zip' missing Runtime property does not raise an error.
    (The current implementation does not enforce a required Runtime for ZIP packages.)"""
    # Calling validate() should not raise an exception even if Runtime is missing.
    Function(
        "TestFunction",
        Code=Code(ZipFile="exports.handler = lambda event: None"),
        PackageType="Zip",
        Role=GetAtt("LambdaExecutionRole", "Arn"),
        Handler="index.handler"
    ).validate()

def test_image_config_invalid_types():
    """Test that ImageConfig raises an error if non-list types are provided for Command or EntryPoint."""
    with pytest.raises(TypeError):
        ImageConfig(Command="not a list").validate()
    with pytest.raises(TypeError):
        ImageConfig(EntryPoint="not a list").validate()