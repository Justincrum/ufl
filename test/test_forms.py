#!/usr/bin/env python

__authors__ = "Martin Sandve Alnes"
__date__ = "2008-03-12 -- 2008-12-02"

# Modified by Anders Logg, 2008

from ufltestcase import UflTestCase, main

from ufl import *
from ufl.algorithms import *

class TestMeasure(UflTestCase):

    def test_manually_constructed_measures(self):
        # Since we can't write 'dx = dx[data]' in a non-global scope,
        # because of corner cases in the python scope rules,
        # it may be convenient to construct measures directly:
        domain_data = ('Stokes', 'Darcy')
        dx = Measure('dx')[domain_data]
        ds = Measure('ds')[domain_data]
        dS = Measure('dS')[domain_data]

        # Possible PyDOLFIN syntax:
        #ds = boundaries.dx(3) # return Measure('dx')[self](3)

    def test_functionals_with_compiler_data(self):
        x, y, z = tetrahedron.x

        a0 = x*dx(0)             + y*dx(0)             + z*dx(1)
        a1 = x*dx(0, {'k': 'v'}) + y*dx(0, {'k': 'v'}) + z*dx(1, {'k': 'v'})
        a2 = x*dx(0, {'k': 'x'}) + y*dx(0, {'k': 'y'}) + z*dx(1, {'k': 'z'})

        b0 = x*dx(0)             + z*dx(1)             + y*dx(0)
        b1 = x*dx(0, {'k': 'v'}) + z*dx(1, {'k': 'v'}) + y*dx(0, {'k': 'v'})
        b2 = x*dx(0, {'k': 'x'}) + z*dx(1, {'k': 'z'}) + y*dx(0, {'k': 'y'})

        c0 = y*dx(0)             + z*dx(1)             + x*dx(0)
        c1 = y*dx(0, {'k': 'v'}) + z*dx(1, {'k': 'v'}) + x*dx(0, {'k': 'v'})
        c2 = y*dx(0, {'k': 'y'}) + z*dx(1, {'k': 'z'}) + x*dx(0, {'k': 'x'})

        d0 = (x*dx(0, {'k': 'xk', 'q':'xq'})
            + y*dx(1, {'k': 'yk', 'q':'yq'}) )
        d1 = (y*dx(1, {'k': 'yk', 'q':'yq'})
            + x*dx(0, {'k': 'xk', 'q':'xq'}))

        a0s = a0.compute_form_data().signature
        a1s = a1.compute_form_data().signature
        a2s = a2.compute_form_data().signature
        b0s = b0.compute_form_data().signature
        b1s = b1.compute_form_data().signature
        b2s = b2.compute_form_data().signature
        c0s = c0.compute_form_data().signature
        c1s = c1.compute_form_data().signature
        c2s = c2.compute_form_data().signature
        d0s = d0.compute_form_data().signature
        d1s = d1.compute_form_data().signature

        # Check stability w.r.t. ordering of terms without compiler data
        self.assertEqual(a0s, b0s)
        self.assertEqual(a0s, c0s)

        # Check stability w.r.t. ordering of terms with equal compiler data
        self.assertEqual(a1s, b1s)
        self.assertEqual(a1s, c1s)

        # Check stability w.r.t. ordering of terms with different compiler data
        self.assertEqual(a2s, b2s)
        self.assertEqual(a2s, c2s)

        # Check stability w.r.t. ordering of terms with two-value compiler data dict
        self.assertEqual(d0s, d1s)

    def test_forms_with_compiler_data(self):
        element = FiniteElement("Lagrange", triangle, 1)

        u = TrialFunction(element)
        v = TestFunction(element)

        # Three terms on the same subdomain using different representations
        a_0 = (u*v*dx(0, {"representation":"tensor"})
               + inner(grad(u), grad(v))*dx(0, {"representation": "quadrature"})
               + inner(grad(u), grad(v))*dx(0, {"representation": "auto"}))

        # Three terms on different subdomains using different representations and order
        a_1 = (inner(grad(u), grad(v))*dx(0, {"representation":"tensor",
                                              "quadrature_degree":8})
               + inner(grad(u), grad(v))*dx(1, {"representation":"quadrature",
                                                "quadrature_degree":4})
               + inner(grad(u), grad(v))*dx(1, {"representation":"auto",
                                                "quadrature_degree":"auto"}))

        # Sum of the above
        a = a_0 + a_1

        # Same forms with no compiler data:
        b_0 = (u*v*dx(0)
               + inner(grad(u), grad(v))*dx(0)
               + inner(grad(u), grad(v))*dx(0))
        b_1 = (inner(grad(u), grad(v))*dx(0)
               + inner(grad(u), grad(v))*dx(1)
               + inner(grad(u), grad(v))*dx(1))
        b = b_0 + b_1

        # Same forms with same compiler data but different ordering of terms
        c_0 = (inner(grad(u), grad(v))*dx(0, {"representation": "auto"})
               + inner(grad(u), grad(v))*dx(0, {"representation": "quadrature"})
               + u*v*dx(0, {"representation":"tensor"}))
        c_1 = (inner(grad(u), grad(v))*dx(0, {"representation":"tensor",
                                              "quadrature_degree":8})
               + inner(grad(u), grad(v))*dx(1, {"representation":"auto",
                                                "quadrature_degree":"auto"})
               + inner(grad(u), grad(v))*dx(1, {"representation":"quadrature",
                                                "quadrature_degree":4}))
        c = c_0 + c_1

        afd = a.compute_form_data()
        cfd = c.compute_form_data()
        bfd = b.compute_form_data()

        self.assertNotEqual(afd.signature, bfd.signature)
        self.assertEqual(afd.signature, cfd.signature)


    def test_measures_with_domain_data(self):
        # Configure measure with some arbitrary data object as domain_data
        domain_data = ('Stokes', 'Darcy')
        dX = dx[domain_data]

        # Build form with this domain_data
        element = FiniteElement("Lagrange", triangle, 1)
        f = Coefficient(element)
        a = f*dX(0) + f**2*dX(1)

        # Check that we get an UFL error when using dX without domain id
        self.assertRaises(UFLException, lambda: f*dX)
        # Check that we get a Python error when using unsupported type
        self.assertRaises(TypeError, lambda: "foo"*dX(1))

        # Check that we get the right domain_data from the preprocessed form data
        fd = a.compute_form_data()
        self.assertIs(fd.domain_data['cell'], domain_data)
        self.assertIsNone(fd.domain_data.get('exterior_facet'))

        # Check that integral_data list is consistent as well
        f2 = f.reconstruct(count=0)
        self.assertIs(fd.domain_data['cell'], domain_data)
        for itd in fd.integral_data:
            self.assertEqual(itd.domain_type, 'cell')
            self.assertEqual(itd.metadata, {})

            if isinstance(itd.domain_id, int):
                self.assertEqual(replace(itd.integrals[0].integrand(), fd.function_replace_map), f2**(itd.domain_id+1))
            else:
                self.assertEqual(itd.domain_id, Measure.DOMAIN_ID_OTHERWISE)

    def test_measure_sums(self):
        element = FiniteElement("Lagrange", triangle, 1)
        f = Coefficient(element)

        a1 = f**2*dx(0) + f**2*dx(3)
        a2 = f**2*(dx(0) + dx(3))
        self.assertEqual(a1, a2)

        a3 = f**2*dx(3) + f**2*dx(0)
        a4 = f**2*(dx(3) + dx(0))
        self.assertEqual(a3, a4)

        # Shouldn't we have sorting of integrals?
        #self.assertEqual(a1, a4)

class TestIntegrals(UflTestCase):

    def test_separated_dx(self):
        "Tests automatic summation of integrands over same domain."
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        f = Coefficient(element)
        a = f*v*dx(0) + 2*v*ds + 3*v*dx(0) + 7*v*ds + 3*v*dx(2) + 7*v*dx(2)
        b = (f*v + 3*v)*dx(0) + (2*v + 7*v)*ds + (3*v + 7*v)*dx(2)
        # Check that integrals are represented canonically after preprocessing
        # (these forms have no indices with icky numbering issues)
        self.assertEqual(a.compute_form_data().preprocessed_form.integrals(),
                         b.compute_form_data().preprocessed_form.integrals())
        # And therefore the signatures should be the same
        self.assertEqual(a.deprecated_signature(), b.deprecated_signature())

    def test_adding_zero(self):
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        a = v*dx
        b = a + 0
        self.assertEqual(id(a), id(b))
        b = 0 + a
        self.assertEqual(id(a), id(b))
        b = sum([a, 2*a])
        self.assertEqual(b, a+2*a)

class TestFormScaling(UflTestCase):

    def test_scalar_mult_form(self):
        D = Domain(triangle)
        R = FiniteElement("Real", D, 0)
        element = FiniteElement("Lagrange", D, 1)
        v = TestFunction(element)
        f = Coefficient(element)
        c = Coefficient(R)
        # These should be acceptable:
        #self.assertEqual(0*(c*dx), (0*c)*dx) # TODO: Need argument annotation of zero to make this work
        self.assertEqual(0*(c*dx(D)), (0*c)*dx(D))
        self.assertEqual(3*(v*dx), (3*v)*dx)
        self.assertEqual(3.14*(v*dx), (3.14*v)*dx)
        self.assertEqual(c*(v*dx), (c*v)*dx)
        self.assertEqual((c**c+c/3)*(v*dx), ((c**c+c/3)*v)*dx)
        # These should not be acceptable:
        self.assertRaises(TypeError, lambda: f*(v*dx))
        self.assertRaises(TypeError, lambda: (f/2)*(v*dx))
        self.assertRaises(TypeError, lambda: (c*f)*(v*dx))

    def test_action_mult_form(self):
        V = FiniteElement("CG", triangle, 1)
        u = TrialFunction(V)
        v = TrialFunction(V)
        f = Coefficient(V)
        a = u*v*dx
        self.assertEqual(a*f, action(a,f))
        self.assertRaises(TypeError, lambda: a*"foo")


class TestExampleForms(UflTestCase):

    def test_source1(self):
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        f = Coefficient(element)
        a = f*v*dx

    def test_source2(self):
        element = VectorElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        f = Coefficient(element)
        a = dot(f,v)*dx

    def test_source3(self):
        element = TensorElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        f = Coefficient(element)
        a = inner(f,v)*dx

    def test_source4(self):
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        x = triangle.x
        f = sin(x[0])
        a = f*v*dx


    def test_mass1(self):
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        u = TrialFunction(element)
        a = u*v*dx

    def test_mass2(self):
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        u = TrialFunction(element)
        a = u*v*dx

    def test_mass3(self):
        element = VectorElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        u = TrialFunction(element)
        a = dot(u,v)*dx

    def test_mass4(self):
        element = TensorElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        u = TrialFunction(element)
        a = inner(u,v)*dx


    def test_point1(self):
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        u = TrialFunction(element)
        a = u*v*dP(0)


    def test_stiffness1(self):
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        u = TrialFunction(element)
        a = dot(grad(u), grad(v)) * dx

    def test_stiffness2(self):
        element = FiniteElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        u = TrialFunction(element)
        a = inner(grad(u), grad(v)) * dx

    def test_stiffness3(self):
        element = VectorElement("Lagrange", triangle, 1)
        v = TestFunction(element)
        u = TrialFunction(element)
        a = inner(grad(u), grad(v)) * dx


    def test_nonnabla_stiffness_with_conductivity(self):
        velement = VectorElement("Lagrange", triangle, 1)
        telement = TensorElement("Lagrange", triangle, 1)
        v = TestFunction(velement)
        u = TrialFunction(velement)
        M = Coefficient(telement)
        a = inner(grad(u)*M.T, grad(v)) * dx

    def test_nabla_stiffness_with_conductivity(self):
        velement = VectorElement("Lagrange", triangle, 1)
        telement = TensorElement("Lagrange", triangle, 1)
        v = TestFunction(velement)
        u = TrialFunction(velement)
        M = Coefficient(telement)
        a = inner(M*nabla_grad(u), nabla_grad(v)) * dx


    def test_nonnabla_navier_stokes(self):
        cell = triangle
        velement = VectorElement("Lagrange", cell, 2)
        pelement = FiniteElement("Lagrange", cell, 1)
        TH = velement * pelement

        v, q = TestFunctions(TH)
        u, p = TrialFunctions(TH)

        f = Coefficient(velement)
        w = Coefficient(velement)
        Re = Constant(cell)
        dt = Constant(cell)

        a = (dot(u, v) + dt*dot(grad(u)*w, v)
            - dt*Re*inner(grad(u), grad(v))
            + dt*dot(grad(p), v))*dx
        L = dot(f, v)*dx
        b = dot(u, grad(q))*dx

    def test_nabla_navier_stokes(self):
        cell = triangle
        velement = VectorElement("Lagrange", cell, 2)
        pelement = FiniteElement("Lagrange", cell, 1)
        TH = velement * pelement

        v, q = TestFunctions(TH)
        u, p = TrialFunctions(TH)

        f = Coefficient(velement)
        w = Coefficient(velement)
        Re = Constant(cell)
        dt = Constant(cell)

        a = (dot(u, v) + dt*dot(dot(w,nabla_grad(u)), v)
            - dt*Re*inner(grad(u), grad(v))
            + dt*dot(grad(p), v))*dx
        L = dot(f, v)*dx
        b = dot(u, grad(q))*dx


if __name__ == "__main__":
    main()
