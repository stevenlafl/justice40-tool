import glob
import os

import yamale
import yaml

UTILS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATA_SET_DESCRIPTIONS_DIRECTORY = os.path.join(
    UTILS_DIRECTORY, "../data_set_descriptions"
)

# TODO: This is hacky for now. Add some safety around loading this, e.g. by
# using `importlib_resources`. - Lucas
DATA_SET_DESCRIPTION_SCHEMA_FILE_PATH = os.path.join(UTILS_DIRECTORY,
                                          "../data_set_description_schema.yaml")
DATA_SET_DESCRIPTION_FIELD_DESCRIPTIONS_FILE_PATH = os.path.join(UTILS_DIRECTORY,
                                      "../data_set_description_field_descriptions.yaml")

DATA_SET_DESCRIPTION_TEMPLATE_FILE_PATH = os.path.join(os.path.dirname(
    os.path.dirname(
    os.path.realpath(__file__))),"data_set_description_template.yaml")


def load_data_set_description_schema():
    schema = yamale.make_schema(path=DATA_SET_DESCRIPTION_SCHEMA_FILE_PATH    )

    return schema

def load_data_set_description_field_descriptions():
    # Load field descriptions.
    with open(DATA_SET_DESCRIPTION_FIELD_DESCRIPTIONS_FILE_PATH, 'r') as stream:
        data_set_description_field_descriptions = yaml.safe_load(stream=stream)

    return data_set_description_field_descriptions

def validate_schema(data_set_description_schema: yamale.schema.schema.Schema,
                    data_set_description_field_descriptions: dict):
    for field_name in data_set_description_schema.dict.keys():
        if field_name not in data_set_description_field_descriptions:
            raise ValueError(f"Field `{field_name}` does not have a "
                             f"description. Please add one to file `{DATA_SET_DESCRIPTION_FIELD_DESCRIPTIONS_FILE_PATH}`")
    pass


def validate_all_data_set_descriptions(data_set_description_schema):
    all_combined_file_paths = sorted(
        glob.glob(os.path.join(DATA_SET_DESCRIPTIONS_DIRECTORY, "*.yaml"))
    )

    # Validate each file
    for file_path in sorted(all_combined_file_paths):
        print(f"Validating {file_path}...")

        # Create a yamale Data object
        data_set_description = yamale.make_data(file_path)

        yamale.validate(schema=data_set_description_schema, data=data_set_description)


def write_data_set_description_template_file(data_set_description_schema, data_set_description_field_descriptions):

    template_file_lines = []

    schema_dict = data_set_description_schema.dict
    for field_name, field_schema in schema_dict.items():
        template_file_lines.append(f"{field_name}: \n")
        template_file_lines.append(f"# Description: {data_set_description_field_descriptions[field_name]}\n")
        template_file_lines.append(f"# Required field: {field_schema.is_required}\n")
        template_file_lines.append(f"# Field type: {field_schema.get_name()}\n")
        if type(field_schema) is yamale.validators.validators.Enum:
            template_file_lines.append(
                f"# Valid choices are one of the following: {field_schema.enums}\n"
            )

        # Add an empty linebreak to separate fields.
        template_file_lines.append("\n")

    with open(DATA_SET_DESCRIPTION_TEMPLATE_FILE_PATH, 'w') as file:
        file.writelines(template_file_lines)


if __name__ == "__main__":
    data_set_description_schema = load_data_set_description_schema()
    data_set_description_field_descriptions = \
        load_data_set_description_field_descriptions()

    validate_schema(data_set_description_schema=data_set_description_schema,
                    data_set_description_field_descriptions=data_set_description_field_descriptions)

    write_data_set_description_template_file(
        data_set_description_schema=data_set_description_schema,
        data_set_description_field_descriptions=data_set_description_field_descriptions)

    validate_all_data_set_descriptions(data_set_description_schema=data_set_description_schema)
