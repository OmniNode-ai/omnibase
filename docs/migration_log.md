# Migration Log: Foundation to ONEX/OmniBase

This log tracks the incremental migration of legacy foundation files to canonical ONEX/OmniBase locations. Update this log as each file is ported, refactored, or removed from the legacy/ directory.

| Legacy File                          | New Canonical Location                        | Status   | Notes | Reviewer |
|--------------------------------------|-----------------------------------------------|----------|-------|----------|
| legacy/registry/base_registry.py     | src/omnibase/core/core_registry.py            | ported   | Initial migration for milestone zero |          |
| legacy/registry/cli_registry.py      | src/omnibase/core/core_cli_registry.py        | ported   | Initial migration for milestone zero |          |
| legacy/registry/utility_registry.py  | src/omnibase/core/core_utility_registry.py    | ported   | Initial migration for milestone zero |          |
| legacy/protocol/protocol_registry.py | src/omnibase/protocol/protocol_registry.py    | ported   | Initial migration for milestone zero |          |
| legacy/protocol/protocol_validate.py | src/omnibase/protocol/protocol_validate.py    | ported   | Initial migration for milestone zero |          |
| legacy/protocol/protocol_cli.py      | src/omnibase/protocol/protocol_cli.py         | ported   | Initial migration for milestone zero |          |
| legacy/protocol/protocol_logger.py   | src/omnibase/protocol/protocol_logger.py      | ported   | Initial migration for milestone zero |          |
| legacy/model/model_metadata.py       | src/omnibase/model/model_metadata.py           | ported   | Initial migration for milestone zero |          |
| legacy/model/model_unified_result.py | src/omnibase/model/model_unified_result.py     | ported   | Initial migration for milestone zero |          |
| legacy/test/validate/metadata/test_metadata_registry_template.py | tests/core/test_registry.py | ported | Initial migration for milestone zero | |
| legacy/template/python/python_test_base_validator.py | docs/templates/template_validator.py | ported | Initial migration for milestone zero | |
| legacy/protocol/protocol_stamper.py | src/omnibase/protocol/protocol_stamper.py | ported | Initial migration for milestone zero | |
| legacy/protocol/protocol_tool.py | src/omnibase/protocol/protocol_tool.py | ported | Initial migration for milestone zero | |
| legacy/protocol/protocol_testable_cli.py | src/omnibase/protocol/protocol_testable_cli.py | ported | Initial migration for milestone zero | |
| legacy/model/model_validate_error.py | src/omnibase/model/model_validate_error.py | ported | Initial migration for milestone zero | |
| legacy/model/model_result_cli.py | src/omnibase/model/model_result_cli.py | ported | Initial migration for milestone zero | |
| legacy/template/validate/validate_template_validator.py | docs/templates/template_validate_validator.py | ported | Initial migration for milestone zero | | 