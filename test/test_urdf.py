from __future__ import print_function

from os.path import abspath, dirname, join
import unittest
import sys
from xml.dom import minidom  # noqa

import mock

# Add path to import xml_matching
# TODO(eacousineau): Can CTest somehow provide this?
TEST_DIR = dirname(abspath(__file__))
sys.path.append(TEST_DIR)
sys.path.append(join(dirname(TEST_DIR), 'src'))

from urdf_parser_py import urdf  # noqa
from xml_matching import xml_matches  # noqa


class ParseException(Exception):
    pass


class TestURDFParser(unittest.TestCase):
    @mock.patch('urdf_parser_py._xml_reflection.on_error',
                mock.Mock(side_effect=ParseException))
    def parse(self, xml):
        return urdf.Robot.from_xml_string(xml)

    def parse_and_compare(self, orig):
        xml = minidom.parseString(orig)
        robot = urdf.Robot.from_xml_string(orig)
        rewritten = minidom.parseString(robot.to_xml_string())
        self.assertTrue(xml_matches(xml, rewritten))

    def test_new_transmission(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="foo_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="foo_motor">
      <mechanicalReduction>50.0</mechanicalReduction>
    </actuator>
  </transmission>
</robot>'''
        self.parse_and_compare(xml)

    def test_new_transmission_multiple_joints(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="foo_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
    <joint name="bar_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="foo_motor">
      <mechanicalReduction>50.0</mechanicalReduction>
    </actuator>
  </transmission>
</robot>'''
        self.parse_and_compare(xml)

    def test_new_transmission_multiple_actuators(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="foo_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="foo_motor">
      <mechanicalReduction>50.0</mechanicalReduction>
    </actuator>
    <actuator name="bar_motor"/>
  </transmission>
</robot>'''
        self.parse_and_compare(xml)

    def test_new_transmission_missing_joint(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
  </transmission>
</robot>'''
        self.assertRaises(Exception, self.parse, xml)

    def test_new_transmission_missing_actuator(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="simple_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="foo_joint">
      <hardwareInterface>EffortJointInterface</hardwareInterface>
    </joint>
  </transmission>
</robot>'''
        self.assertRaises(Exception, self.parse, xml)

    def test_old_transmission(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <transmission name="PR2_trans" type="SimpleTransmission">
    <joint name="foo_joint"/>
    <actuator name="foo_motor"/>
    <mechanicalReduction>1.0</mechanicalReduction>
  </transmission>
</robot>'''
        self.parse_and_compare(xml)

    def test_link_material_missing_color_and_texture(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <link name="link">
    <visual>
      <geometry>
        <cylinder length="1" radius="1"/>
      </geometry>
      <material name="mat"/>
    </visual>
  </link>
</robot>'''
        self.parse_and_compare(xml)

    def test_robot_material(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <material name="mat">
    <color rgba="0.0 0.0 0.0 1.0"/>
  </material>
</robot>'''
        self.parse_and_compare(xml)

    def test_robot_material_missing_color_and_texture(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <material name="mat"/>
</robot>'''
        self.assertRaises(ParseException, self.parse, xml)


class LinkOriginTestCase(unittest.TestCase):
    @mock.patch('urdf_parser_py._xml_reflection.on_error',
                mock.Mock(side_effect=ParseException))
    def parse(self, xml):
        return urdf.Robot.from_xml_string(xml)

    def test_robot_link_defaults(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <link name="test_link">
    <inertial>
      <mass value="10.0"/>
      <origin/>
    </inertial>
  </link>
</robot>'''
        robot = self.parse(xml)
        origin = robot.links[0].inertial.origin
        self.assertEquals(origin.xyz, [0, 0, 0])
        self.assertEquals(origin.rpy, [0, 0, 0])

    def test_robot_link_defaults_xyz_set(self):
        xml = '''<?xml version="1.0"?>
<robot name="test">
  <link name="test_link">
    <inertial>
      <mass value="10.0"/>
      <origin xyz="1 2 3"/>
    </inertial>
  </link>
</robot>'''
        robot = self.parse(xml)
        origin = robot.links[0].inertial.origin
        self.assertEquals(origin.xyz, [1, 2, 3])
        self.assertEquals(origin.rpy, [0, 0, 0])


class TestExampleRobots(unittest.TestCase):
    """Tests that some samples files can be parsed without error."""
    @unittest.skip("Badly formatted transmissions")
    def test_calvin_urdf(self):
        urdf.Robot.from_xml_file(join(TEST_DIR, 'calvin/calvin.urdf'))

    def test_romeo_urdf(self):
        urdf.Robot.from_xml_file(join(TEST_DIR, 'romeo/romeo.urdf'))


if __name__ == '__main__':
    unittest.main()
