#!/usr/bin/env python

import rospy

from std_msgs.msg import Float64

from joint_angle import JointAngle
from recording import Recording

class DirectDrive:
    def __init__(self, name, servoRange):
        self.name = name
        self.servoRange = servoRange
        self.initPublishers()
        self.initVariables()

        self.angle = JointAngle(name, 1, -servoRange/2, servoRange/2, False)
        self.recording = Recording()

    def initPublishers(self):
        self.pub = rospy.Publisher(self.name + '_controller/command', Float64, queue_size=5)

    def initVariables(self):
        self.velocity = False
        self.noCommandYet = True

    def servoTo(self, dAngle):
        self.velocity = False
        self.angle.setDesired(dAngle)
        self.noCommandYet = False
        self.doUpdate()

    def servoWith(self, dVelocity):
        self.velocity = True
        self.angle.setDesiredVelocity(dVelocity)
        self.noCommandYet = False
        self.doUpdate()

    def publishCommand(self):
        dAngle = self.angle.getDesired()
        self.pub.publish(dAngle)

    def doUpdate(self):
        if self.velocity:
            self.angle.doVelocityIncrement()
            
        if self.noCommandYet:
            self.angle.setDesired(self.encoderAngle)
            
        self.publishCommand()

    def getJointAngle(self):
        return self.angle.getEncoder()

    def prepareRecording(self, fileNameBase):
        fileName = fileNameBase + "_" + self.name + ".csv"
        self.recording.prepare(fileName, ['time','angle'])

    def recordLine(self, delta):
        angle = self.getJointAngle()
        self.recording.add([delta, angle])
