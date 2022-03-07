from util import check_compiles


def test_function():
    input = """<?php
        function foo() {
            echo "bar";
        }
        foo();
    """
    expected = "def foo():\n" "    echo('bar')\n" "foo()"
    check_compiles(input, expected)


def test_function_with_args():
    input = """<?php
        function foo($bar) {
            echo $bar;
        }
        foo();
    """
    expected = "def foo(bar):\n" "    echo(bar)\n" "foo()"
    check_compiles(input, expected)


def test_more_function_calls():
    input = r"""<?php
        # doit($arg1, &$arg2, 3 + 4);
        name\spaced();
        \name\spaced();
        namespace\d();
    ?>"""
    # FIXME: namespaces
    expected = "name()\n" "name()\n" "d()"
    check_compiles(input, expected)


def xtest_function2():
    input = """<?php
        /**
         * search an available feed_id
         *
         * @return string feed identifier
         */
        function find_available_feed_id() {
          while (true) {
            $key = generate_key(50);
            $query = '
                SELECT COUNT(*)
                  FROM '.USER_FEED_TABLE.'
                  WHERE id = \''.$key.'\'
                ;';
            list($count) = pwg_db_fetch_row(pwg_query($query));
            if (0 == $count) {
              return $key;
            }
          }
        }
    """
    expected = ""
    check_compiles(input, expected)
