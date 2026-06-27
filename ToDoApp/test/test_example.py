import pytest
# assert if used to validating some data against other
#  test only passes if all asserts passed, both are under one test
def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1
#     assert not isinstance('10', int)  passes only if it is not integer
#     assert type('World') is not int

def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('this is a string' , int)


def test_boolean():
    validated = True
    assert validated is True
    assert ('Hello' == 'world') is False


def test_type():
    assert type('Hello' is str)
    assert type('Hello' is not int)


def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10


def test_list():
    num_list = [1,2,3,4]
    lst = [False, False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)   #“All should be True to pass, Fail the test if ANY element in the list is falsy (like 0, None, or False).”
    # assert any(lst)  # “At least one should be True to pass, this will fail
    assert not any(lst) #any will always return true if onr or more is true and will only return false if all are false , so with not,  test passes only if all elements are falsy


class Student:
    def __init__(self, first_name:str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


def test_person_intialization():
    p = Student('John' , 'Doe' , 'Computer Science', 3) # instantiating new object everytime for each test that needs a student ->>> solved by pytest fixtures
    assert p.first_name == 'John' , 'First Name should be John' # message is optional to inform other developers
    assert p.last_name == 'Doe'
    assert p.major == 'Computer Science'
    assert p.years == 3


@pytest.fixture
def default_employee():
    return Student('John' , 'Doe' , 'Computer Science', 3)


# passing dependency to the test , the dependency is injected automatically --->> Give the test some object/data/service that it needs, instead of creating it inside the test."
def test_person_intialization_with_fixture(default_employee):
    assert default_employee.first_name == 'John' , 'First Name should be John' # message is optional to inform other developers
    assert default_employee.last_name == 'Doe'
    assert default_employee.major == 'Computer Science'
    assert default_employee.years == 3