import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32MultiArray
from geometry_msgs.msg import Twist, Vector3
from rcl_interfaces.msg import ParameterDescriptor, FloatingPointRange, SetParametersResult
from std_srvs.srv import Trigger

# Create the main class for entry
class ESCs(Node):
    def __init__(self):
        super().__init__('ESCs')


        # Get the logger
        self.log = self.get_logger()

        # Declare pwm frequency
        self.pwm_frequency = 100
        self.initial_duty = 0.15
        
        # Creates the subscriber and publisher
        self.thruster_sub = self.create_subscription(Twist, 'cmd_vel', self.thruster_callback, 10)
        self.thruster_status_sub = self.create_subscription(Bool, 'thruster_status', self.thruster_status_callback, 10)

        self.pwm_pub = self.create_publisher(Float32MultiArray, 'ESC_pwm_input', 10)

        # Define slider parameters
        slider_bounds = FloatingPointRange()
        slider_bounds.from_value = 0.0
        slider_bounds.to_value = 1.0
        slider_bounds.step = 0.025
        slider_descriptor = ParameterDescriptor(floating_point_range = [slider_bounds])

        # Tells the thrusters whether they're allowed to spin or not
        self.thrusters_enabled = False

        # Last thruster values to prevent ESC reset
        self.last_thrusters = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15]

        # Max delta of thrusters
        self.max_delta = 0.004

    # Runs whenever /cmd_vel topic recieves a new twist msg
    # Twist msg reference: http://docs.ros.org/en/noetic/api/geometry_msgs/html/msg/Twist.html
    def thruster_status_callback(self, msg):
        self.thrusters_enabled = msg.data

    def thruster_callback(self, msg):    

        linearX = msg.linear.x
        linearY = msg.linear.y 
        linearZ = msg.linear.z
        angularX = msg.angular.x
        angularZ = msg.angular.z

        # Scalar to limit each thruster to 1800 Hz
        scalar = 0.75

        # Decompose the vectors into thruster values
        # linearX references moving along X-axis, or forward
        # angularZ referneces rotation around vertical axis, or Z-axis.
        # For more reference directions, see https://www.canva.com/design/DAFyPqmH8LY/2oMLLaP8HHGi2e07Ms8fug/view
        msglist = [(linearX - linearY - angularZ)  * scalar,
                   (linearX + linearY + angularZ)  * scalar,
                   (-linearX - linearY + angularZ) * scalar,
                   (-linearX + linearY - angularZ) * scalar,
                   (-linearZ - angularX) * scalar,
                   (-linearZ + angularX) * scalar]

        # function to limit a value between -1 and 1
        # min(value, 1) takes the returns lesser of the two values. So if value is greater than 1, it returns 1.
        def limit_value(value):
            return max(-0.95, min(value, 0.95))

        # Use map() to apply the limit_value function to each element of msglist
        msglist = list(map(limit_value, msglist))

        dutylist = [ round(0.15 - msglist[i] / 25, 5) for i in range(6) ]

        # Loop to prevent ESC reset
        # We make sure that the thrusters' speed can only change by a given amount each interval so as to not overwhelm them.
        for i in range(6):
            if self.thrusters_enabled:
                if abs(dutylist[i] - self.last_thrusters[i]) > self.max_delta:
                    if dutylist[i] > self.last_thrusters[i]:
                        dutylist[i] = self.last_thrusters[i] + self.max_delta
                    else:
                        dutylist[i] = self.last_thrusters[i] - self.max_delta

                self.last_thrusters[i] = dutylist[i]

            else:
                self.last_thrusters[i] = 0.15

        # Formulas:
        # pulse width = duty * period
        # period = 1/frequency (frequency must be converted to cycles/microsecond)
        # At 100 Hz, period = 10000 microseconds
        
        # Publish array of pulse widths
        pwm_msg = Float32MultiArray(data=[d * 10000 for d in self.last_thrusters])
        self.pwm_pub.publish(pwm_msg)
        self.log.info(str(pwm_msg))
       
# Runs the node
def main(args=None):
    rclpy.init(args=args)

    escs = ESCs()

    rclpy.spin(escs)
    
    escs.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
   main()
