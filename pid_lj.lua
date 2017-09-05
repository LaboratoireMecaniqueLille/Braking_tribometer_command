-- PID variables
timeStep = 1 --ms
inputV = 0
setpoint = 0
outV = 0

-- PI values for force loop
kpf = 0.002
kif = 5
kif = kpf*kif*timeStep/1000

-- PI values for torque loop
kpc = 0.008
kic = 3
kic = kpc*kic*timeStep/1000

polOut = -1  --output polarity +1 or -1, i.e. for a positive error, negative output: -1

outMin = -10  --bounds for the output value
outMax = 10

intterm = 0
iMax = .05
iMin = -.05

LJ.IntervalConfig(0, timeStep)

MB.W(30002, 3, 0) --Set TDAC1 to 0 (for a good start)

--i = 0
while true do
  if LJ.CheckInterval(0) then
    if MB.R(46002, 3) ~= 0 then
      setpoint = MB.R(46000, 3) --get new setpoint from USER_RAM0_F32, address 46000
      if MB.R(46002, 3) == 1 then -- Force mode
        inputV = MB.R(0, 3)*2061.3+110  --read AIN0, turn it to N (Applying offset!)
        kp = kpf
        ki = kif
      elseif MB.R(46002,3) == 2 then
        inputV = MB.R(4, 3)*-50 -- Read AIN2, turn it to Nm
        kp = kpc
        ki = kic
      end
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
    else
      intterm = 0
      MB.W(30002, 3, 0) --Set TDAC1 to 0
    end
  end
end
