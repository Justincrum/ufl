# Copyright (C) 2008-2014 Andrew T. T. McRae
#
# This file is part of UFL.
#
# UFL is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UFL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with UFL. If not, see <http://www.gnu.org/licenses/>.
#
# First added:  2013-11-03
# Last changed: 2014-03-18

from ufl.finiteelement.outerproductelement import OuterProductElement


class HDiv(OuterProductElement):
    """A div-conforming version of an outer product element, assuming
    this makes mathematical sense."""
    __slots__ = ("_element")

    def __init__(self, element):
        self._element = element
        self._repr = "HDiv(%s)" % str(element._repr)

        family = "OuterProductElement"
        domain = element.domain()
        degree = element.degree()
        quad_scheme = element.quadrature_scheme()
        value_shape = (element.cell().geometric_dimension(),)
        super(OuterProductElement, self).__init__(family, domain, degree,
                                                  quad_scheme, value_shape)

    def reconstruction_signature(self):
        return "HDiv(%s)" % self._element.reconstruction_signature()

    def signature_data(self, domain_numbering):
        data = ("HDiv", self._element.signature_data(domain_numbering=domain_numbering),
                ("no domain" if self._domain is None else self._domain
                    .signature_data(domain_numbering=domain_numbering)))
        return data

    def __str__(self):
        return "HDiv(%s)" % str(self._element)

    def shortstr(self):
        return "HDiv(%s)" % str(self._element.shortstr())

    def __repr__(self):
        return self._repr


class HCurl(OuterProductElement):
    """A curl-conforming version of an outer product element, assuming
    this makes mathematical sense."""
    __slots__ = ("_element")

    def __init__(self, element):
        self._element = element
        self._repr = "HCurl(%s)" % str(element._repr)

        family = "OuterProductElement"
        domain = element.domain()
        degree = element.degree()
        quad_scheme = element.quadrature_scheme()
        value_shape = (element.cell().geometric_dimension(),)
        super(OuterProductElement, self).__init__(family, domain, degree,
                                                  quad_scheme, value_shape)

    def reconstruction_signature(self):
        return "HCurl(%s)" % self._element.reconstruction_signature()

    def signature_data(self, domain_numbering):
        data = ("HCurl", self._element.signature_data(domain_numbering=domain_numbering),
                ("no domain" if self._domain is None else self._domain
                    .signature_data(domain_numbering=domain_numbering)))
        return data

    def __str__(self):
        return "HCurl(%s)" % str(self._element)

    def shortstr(self):
        return "HCurl(%s)" % str(self._element.shortstr())

    def __repr__(self):
        return self._repr
