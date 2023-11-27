"""
common.py
Functions and data entities used by multiple application handler modules in this package.
https://907sjl.github.io/

Public Attributes:
    HEAT_MAP_PALETTE - Colors used in gradient color mapping of referral ages from short term to long term
    AGE_CATEGORY_COLOR_MAP - Dictionary of referral age bins with associated background colors
    AGE_CATEGORY_LABEL_COLOR_MAP - Dictionary of referral age bins with associated text colors

Public Functions:
    half_up_int - Convenience function to round final results half-up
    create_color_mappers - Creates unique color mapper Bokeh instances, Bokeh requires unique instances per document
    add_clinic_slicer - Creates a drop-down widget within a given document containing clinic names
    get_clinic_from_request - Parses the HTTP request and cookies to identify the last selected clinic
"""

from bokeh.document import Document
from bokeh.models import Select

from datetime import datetime

from bokeh.core.property.vectorization import Field
from bokeh.models import LinearColorMapper, CustomJS
from bokeh.transform import factor_cmap

import model.ProcessTime as wt


# reverse heat map color palette
HEAT_MAP_PALETTE = ['#55BCFF', '#AADAFF', '#EAEA6A', '#FDCD66', '#FF9550', '#FD6262'][::-1]

# Histogram color maps using age categories
AGE_CATEGORY_COLOR_MAP = {'7d': '#55BCFF',
                          '14d': '#AADAFF',
                          '30d': '#EAEA6A',
                          '60d': '#FDCD66',
                          '90d': '#FF9550',
                          '>90d': '#FD6262'}

AGE_CATEGORY_LABEL_COLOR_MAP = {'7d': '#000000',
                                '14d': '#000000',
                                '30d': '#000000',
                                '60d': '#000000',
                                '90d': '#000000',
                                '>90d': '#FFFFFF'}


def half_up_int(value: float) -> int:
    """
    Returns an integer value that is rounded half-up.
    :param value: the value to round
    :return: an integer rounded half-up
    """
    if value >= 0:
        return int(value + 0.5)
    else:
        return int(value - 0.5)


# END half_up_int


def create_color_mappers(heat_map_palette,
                         age_category_color_map,
                         age_category_label_color_map) -> tuple[LinearColorMapper, Field, Field]:
    """
    Creates unique color mapper Bokeh instances.  Bokeh requires unique instances per document.
    :param heat_map_palette: The list with the gradient colors for wait times
    :param age_category_color_map: The dictionary with the background colors for each time bin
    :param age_category_label_color_map: The dictionary with the text color for each time bin
    :return: A tuple with three Bokeh color mapper objects
        LinearColorMapper: The gradient color mapper from near term to long term waits
        Field: The background categorical color mapper for wait time bins
        Field: The text categorical color mapper for wait time bins
    """
    # Create Bokeh color mapper model objects for each new document object as
    # required by Bokeh
    percentage_color_mapper = LinearColorMapper(palette=heat_map_palette, low=0, high=1.0, low_color='#808080')
    age_category_color_mapper = (
        factor_cmap('category',
                    palette=list(age_category_color_map.values()),
                    factors=list(age_category_color_map.keys())))
    age_category_label_color_mapper = factor_cmap('category',
                                                  palette=list(age_category_label_color_map.values()),
                                                  factors=list(age_category_label_color_map.keys()))

    return percentage_color_mapper, age_category_color_mapper, age_category_label_color_mapper
# END create_color_mappers


def add_clinic_slicer(doc: Document,
                      month: datetime,
                      clinic: str,
                      *callback) -> None:
    """
    Creates a drop-down widget within a given document containing clinic names
    :param doc: The document to contain the drop-down widget
    :param month: The month to filter the clinic data by when collecting clinic names
    :param clinic: The default selection
    :param callback: The python function to call when the selection changes
    """
    select = Select(value=clinic, options=wt.get_clinics(month))
    select.on_change("value", *callback)

    code = """
        // the model that triggered the callback is cb_obj:
        const v = cb_obj.value;
        document.cookie = "clinic=" + v + "; path=/";
    """
    js_callback = CustomJS(code=code)
    select.js_on_change('value', js_callback)

    select.name = 'clinic_slicer'
    doc.add_root(select)
# END add_clinic_slicer


def get_clinic_from_request(doc: Document) -> str:
    """
    Parses the HTTP request and cookies to identify the last selected clinic
    :param doc: The document created from the HTTP request that contains the clinic parameter and cookies
    :return: Returns the clinic name passed in via HTTP or an empty string if none
    """
    # First grab the clinic name from the HTTP cookies
    cookies = doc.session_context.request.cookies
    if 'clinic' in cookies:
        clinic = cookies['clinic']
        if len(clinic) > 0:
            return clinic

    # Override with the clinic name from the HTTP request arguments
    args = doc.session_context.request.arguments
    if 'Clinic' in args:
        clinic = args['Clinic'][0]
        if len(clinic) > 0:
            clinic = clinic.decode("utf-8")
            return clinic

    return ''
# END get_clinic_from_request
