# languages=PHP
PHP = r"""
final class XmlToPropsParser
{
    private function addCurrentValue($value): void
    {
        switch ($this->lastPropertyType) {
            case PropertyType::NAME:
                $this->currentValues[] = (string) $value;
                break;
        }
    }
}
"""

EXPECTED = ""
