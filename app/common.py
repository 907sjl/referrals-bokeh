"""
common.py
Functions and data entities used by multiple classes.
https://907sjl.github.io/
"""

from bokeh.document import Document
from bokeh.models import Select

from datetime import datetime

from bokeh.core.property.vectorization import Field
from bokeh.models import LinearColorMapper, CustomJS
from bokeh.transform import factor_cmap

import model.WaitTimes as wt


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
