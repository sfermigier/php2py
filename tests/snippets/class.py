# language=php
PHP = r"""
<?php

class Car {
    function Car() {
        $this->model = "Tesla";
    }
}

// create an object
$Lightning = new Car();

// show object properties
echo $Lightning->model;

?>
"""

# EXPECTED = """
# class Car:
#     def __init__(self):
#         self.model = "Tesla"
#
# Lightning = Car()
# print(Lightning.model)
# """
