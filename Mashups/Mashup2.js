const Robot_TD_ADDRESS = "http://192.168.0.105:8080/MeArmPi";
const LightSensor_TD_ADDRESS = "http://192.168.0.102/";
const senseHAT_TD_ADDRESS = "http://192.168.0.106:8080/SenseHat";
const strip_TD_ADDRESS = "http://192.168.0.103:8080/";

WoT.fetch(Robot_TD_ADDRESS).then(async (robotTD) => {
    WoT.fetch(senseHAT_TD_ADDRESS).then(async (senseHatTD) => {
        WoT.fetch(LightSensor_TD_ADDRESS).then(async (lightSensorTD) => {
            robotThing = WoT.consume(robotTD);
            lightSensorThing = WoT.consume(lightSensorTD);
            senseHatThing = WoT.consume(senseHatTD);
            
            setInterval(async () => {
                var intensity = await lightSensorThing.properties.intensity.read();
                if (intensity < 200) {
                    robotThing.actions["closeGrip"].invoke();
                    robotThing.actions["moveBaseTo"].invoke(75);
                    senseHatThing.actions["flashMessage"].invoke({
                        "textString": "<"
                    });
                } else {
                    robotThing.actions["openGrip"].invoke();
                    robotThing.actions["moveBaseTo"].invoke(-75);
                    senseHatThing.actions["flashMessage"].invoke({
                        "textString": ">"
                    });
                }
            }, 200);
        });
    });
})


