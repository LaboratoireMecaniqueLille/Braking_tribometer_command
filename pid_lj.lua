-- PID variables
timeStep = 1 --ms
inputV = 0
setpoint = 0
outV = 0

kp = 0.002
ki = 5

ki = kp*ki*timeStep/1000

polOut = -1  --output polarity +1 or -1, i.e. for a positive error, negative output: -1

outMin = -10  --bounds for the output value
outMax = 10

intterm = 0
iMax = .05
iMin = -.05

LJ.IntervalConfig(0, timeStep)

MB.W(30002, 3, 0) --Set TDAC1

--i = 0
while true do
  if true then --MB.R(46002, 3) == 1 then
    if LJ.CheckInterval(0) then --interval completed
      inputV = MB.R(0, 3)*2061.3+110  --read AIN0, turn it to N (Applying offset!)
      setpoint = MB.R(46000, 3) --get new setpoint from USER_RAM0_F32, address 46000
      --setpoint=600
      err = setpoint - inputV
      --print("error=",err)

      intterm = intterm + ki * err
      if intterm > iMax then
        intterm = iMax
      elseif intterm < iMin then
        intterm = iMin
      end
      --print("    intterm=",intterm)

      outV = polOut* (kp * err + intterm)
      if outV > outMax then
        outV = outMax
      elseif outV < outMin then
        outV = outMin
      end
      --print("  Output=",outputV)
      MB.W(30002, 3, outV) --Set TDAC1
    end
  elseif MB.R(46002, 3) == 0 then
    if LJ.CheckInterval(0) then
      --MB.W(30002, 3, 0)
      intterm = 0
    end
  end
end
