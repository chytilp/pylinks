"""
Lib for checking parameters with webargs.

Example usage::
    from webargs import fields

    ...
    ...
    ...

    class MyResource(Resource):
        @login_required
        @check_rights_any(???)
        @use_args({
            "dateFrom": fields.Int(validate=gte(0)),
            "dateTo": fields.Int(validate=gte(0)),
            "limit": fields.Int(validate=between(1, 100)),
            "next": fields.Int(validate=gte(0))
        })
        def get(self, args):
            dateTo = args.get('dateTo')
            dateFromTimestamp = args.get('dateFrom')
            limit = args.get('limit')
            offset = args.get('next')

"""

from webargs import flaskparser, ValidationError
from marshmallow import validate
import validators
from validators import ValidationFailure

parser = flaskparser.FlaskParser()


@parser.error_handler
def handle_error(err, req, schema, *, error_status_code, error_headers):
    errors = []
    if isinstance(err.messages, dict):
        for location, fielddata in err.messages.items():
            if isinstance(fielddata, dict):
                for key, value in fielddata.items():
                    if isinstance(value, list):
                        errors.append({
                            "argumentName": key,
                            "messages": value
                        })
                    elif isinstance(value, dict):
                        errors.append({
                            "argumentName": key,
                            "itemErrorMessages": value
                        })
                    else:
                        # This case should never happen. If it happens we want to send
                        # at least some error messages even if it isnt compliant with
                        # our error format.
                        errors = err.messages
                        break
            else:
                errors.append({
                    "messages": fielddata
                })
    else:
        errors = [{'messages': [error for error in err.messages]}]

    flaskparser.abort(400, errors=errors, status=400)


use_args = parser.use_args
use_kwargs = parser.use_kwargs


def gt(greater_than):
    """
    Returns function to compare whether `param` is greater than `greater_than`.
    `param` and  `greater_than` must be comparable.
    """
    def gt_impl(param):
        if param <= greater_than:
            raise ValidationError("Parameter must be greater than {}".format(greater_than))
        return True

    return gt_impl


def gte(greater_than_or_equal):
    """
    Returns function to compare whether `param` is greater than or equal to `greater_than`.
    `param` and  `greater_than_or_equal` must be comparable.
    """
    def gte_impl(param):
        if param < greater_than_or_equal:
            raise ValidationError("Parameter must be greater than or equal {}".format(
                greater_than_or_equal))
        return True

    return gte_impl


def lt(less_than):
    """
    Returns function to compare whether `param` is less than `less_than`.
    `param` and  `less_than` must be comparable.
    """
    def lt_impl(param):
        if param >= less_than:
            raise ValidationError("Parameter must be less than {}".format(less_than))
        return True

    return lt_impl


def lte(less_than_or_equal):
    """
    Returns function to compare whether `param` is less than or equal to `less_than_or_equal`.
    `param` and  `less_than_or_equal` must be comparable.
    """
    def lte_impl(param):
        if param > less_than_or_equal:
            raise ValidationError("Parameter must be less than or equal {}".format(
                less_than_or_equal))
        return True

    return lte_impl


def between(greater_than_or_equal, less_than_or_equal):
    """
    Returns function to compare whether `param` is from
    interval [`greater_than_or_equal`, `less_than_or_equal`].
    `param` and  `greater_than_or_equal`, `less_than_or_equal` must be comparable.
    """
    def between_impl(param):
        if param < greater_than_or_equal or param > less_than_or_equal:
            raise ValidationError("Parameter must be from interval [{}..{}]".format(
                greater_than_or_equal, less_than_or_equal))
        return True

    return between_impl


def max_len(max_length):
    """
    Returns function to compare whether `param` is not longer than `max_length`.
    `param` must be valid argument for `len` function.
    """
    def max_len_impl(param):
        len_param = len(param)
        if len_param > max_length:
            raise ValidationError("Parameter length must not be greater then {}. "
                                  "Your parameter has length {}.".format(max_length, len_param))
        return True

    return max_len_impl


def is_email(email):
    """
    checks if email is in valid form
    """
    if (len(email) > 320 or '@' not in email or
            str.find(email, '.', str.find(email, '@') + 2) <= 0):
                raise ValidationError("Wrong email format")
    return True


def is_not_empty(array):
    """
    checks if array is not empty
    """
    if len(array) > 0:
        return True
    else:
        raise ValidationError("Array is empty")


def one_of(set_like):
    """
    marshmallow.validate.OneOf with custom error message that list all possible choices.
    """
    return validate.OneOf(set_like, error="Parameter must be one of: {choices}")


def unique_values(param):
    """
    Check whether List object has only unique values.
    """
    if len(param) != len(set(param)):
        raise ValidationError("List must contain only unique values.")
    return True


def xor_args(arg1, arg2):
    """
    Checks whether one of the parameters is present and not both.
    """
    def xor_args_impl(args_dict):
        xor = bool(args_dict.get(arg1)) ^ bool(args_dict.get(arg2))
        if not xor:
            raise ValidationError(
                "Either parameter {} or parameter {} must be passed.".format(arg1, arg2)
                + " Parameters must not be passed together.")
        return True
    return xor_args_impl


def not_both_args(arg1, arg2):
    """
    Checks whether both of the parameters are not present at once.
    """
    def not_both_args_impl(args_dict):
        and_ = bool(args_dict.get(arg1)) and bool(args_dict.get(arg2))
        if and_:
            raise ValidationError(
                "Parameters {} and {} must not be present at once".format(arg1, arg2))
        return True
    return not_both_args_impl


def is_url(url_string):
    result = validators.url(url_string)

    err_message = "Url address {} is not valid.".format(url_string)
    if isinstance(result, ValidationFailure):
        raise ValidationError(err_message)
    if not result:
        raise ValidationError(err_message)
    return result
