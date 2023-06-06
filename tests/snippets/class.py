# language=php
PHP = r"""
<?php

class Car {
    function Car() {
        $this->model = "Tesla";
    }
    
    function hello($x, $y, $z) {
        return "beep";
    }
}

// create an object
$Lightning = new Car();

// show object properties
echo $Lightning->model;

?>
"""

EXPECTED = """
class Car:
    def __init__(self):
        self.model = "Tesla"

    def hello(self, x, y, z):
        return "beep"


Lightning = Car()
print(Lightning.model)
"""
