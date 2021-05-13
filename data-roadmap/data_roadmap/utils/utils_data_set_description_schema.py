import glob
import os

import yamale
import yaml

import importlib_resources

DATA_ROADMAP_DIRECTORY = importlib_resources.files("data_roadmap")
UTILS_DIRECTORY = DATA_ROADMAP_DIRECTORY.joinpath("utils")
DATA_SET_DESCRIPTIONS_DIRECTORY = DATA_ROADMAP_DIRECTORY.joinpath(
    "data_set_descriptions"
)

DATA_SET_DESCRIPTION_SCHEMA_FILE_PATH = DATA_ROADMAP_DIRECTORY.joinpath(
    "data_set_description_schema.yaml"
)
DATA_SET_DESCRIPTION_FIELD_DESCRIPTIONS_FILE_PATH = DATA_ROADMAP_DIRECTORY.joinpath(
    "data_set_description_field_descriptions.yaml"
)

DATA_SET_DESCRIPTION_TEMPLATE_FILE_PATH = DATA_ROADMAP_DIRECTORY.joinpath(
    "data_set_description_template.yaml"
)


def load_data_set_description_schema(file_path=DATA_SET_DESCRIPTION_SCHEMA_FILE_PATH):
    """Load from file the data set description schema."""
    schema = yamale.make_schema(path=file_path)

    return schema


def load_data_set_description_field_descriptions(
    file_path=DATA_SET_DESCRIPTION_FIELD_DESCRIPTIONS_FILE_PATH,
):
    """Load from file the descriptions of fields in the data set description."""
    # Load field descriptions.
    with open(file_path, "r") as stream:
        data_set_description_field_descriptions = yaml.safe_load(stream=stream)

    return data_set_description_field_descriptions


def validate_descriptions_for_schema(
    schema: yamale.schema.schema.Schema,
    field_descriptions: dict,
):
    """Validate descriptions for schema.

    Checks that every field in the `yamale` schema also has a field
    description in the `field_descriptions` dict.
    """
    for field_name in schema.dict.keys():
        if field_name not in field_descriptions:
            raise ValueError(
                f"Field `{field_name}` does not have a "
                f"description. Please add one to file `{DATA_SET_DESCRIPTION_FIELD_DESCRIPTIONS_FILE_PATH}`"
            )

    for field_name in field_descriptions.keys():
        if field_name not in schema.dict.keys():
            raise ValueError(
                f"Field `{field_name}` has a description but is not in the " f"schema."
            )


def validate_all_data_set_descriptions(
    data_set_description_schema: yamale.schema.schema.Schema,
):
    """Validate data set descriptions.

    Validate each file in the `data_set_descriptions` directory the schema
    against the provided schema.

    """
    data_set_description_file_paths_generator = DATA_SET_DESCRIPTIONS_DIRECTORY.glob(
        "*.yaml"
    )

    # Validate each file
    for file_path in data_set_description_file_paths_generator:
        print(f"Validating {file_path}...")

        # Create a yamale Data object
        data_set_description = yamale.make_data(file_path)

        # TODO: explore collecting all errors and raising them at once. - Lucas
        yamale.validate(schema=data_set_description_schema, data=data_set_description)


def write_data_set_description_template_file(
    data_set_description_schema: yamale.schema.schema.Schema,
    data_set_description_field_descriptions: dict,
    template_file_path: str = DATA_SET_DESCRIPTION_TEMPLATE_FILE_PATH,
):
    """Write an example data set description with helpful comments."""

    template_file_lines = []

    # Write comments at the top of the template
    template_file_lines.append(
        "# Note: This template is automatically generated by the function\n"
        "# `write_data_set_description_template_file` from the schema\n"
        "# and field descriptions files. Do not manually edit this file.\n\n"
    )

    schema_dict = data_set_description_schema.dict
    for field_name, field_schema in schema_dict.items():
        template_file_lines.append(f"{field_name}: \n")
        template_file_lines.append(
            f"# Description: {data_set_description_field_descriptions[field_name]}\n"
        )
        template_file_lines.append(f"# Required field: {field_schema.is_required}\n")
        template_file_lines.append(f"# Field type: {field_schema.get_name()}\n")
        if type(field_schema) is yamale.validators.validators.Enum:
            template_file_lines.append(
                f"# Valid choices are one of the following: {field_schema.enums}\n"
            )

        # Add an empty linebreak to separate fields.
        template_file_lines.append("\n")

    with open(template_file_path, "w") as file:
        file.writelines(template_file_lines)


def run_validations_and_write_template():
    """Run validations of schema and descriptions, and write a template file."""
    # Load the schema and a separate dictionary
    data_set_description_schema = load_data_set_description_schema()
    data_set_description_field_descriptions = (
        load_data_set_description_field_descriptions()
    )

    validate_descriptions_for_schema(
        schema=data_set_description_schema,
        field_descriptions=data_set_description_field_descriptions,
    )

    # Validate all data set descriptions in the directory against schema.
    validate_all_data_set_descriptions(
        data_set_description_schema=data_set_description_schema
    )

    # Write an example template for data set descriptions.
    write_data_set_description_template_file(
        data_set_description_schema=data_set_description_schema,
        data_set_description_field_descriptions=data_set_description_field_descriptions,
    )


if __name__ == "__main__":
    run_validations_and_write_template()
