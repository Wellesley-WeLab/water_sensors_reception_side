"""
Definition of classes representing tables in the database
"""

import MySQLdb
import config


class Measurement () :
    """
    One measurement made by the water sensor
    """

    def __init__ (self, **kwargs) :
        self.packetNr     = kwargs['packetNr']
        self.reservoir    = kwargs['reservoir']
        self.waterGap     = (kwargs['waterGap']*1024/kwargs['vcc'])/100
        self.vcc          = kwargs['vcc']
        self.pH           = kwargs['pH']
        self.conductivity = kwargs['conductivity']/1000
        self.salinity     = kwargs['salinity']/1000
        self.tds          = kwargs['tds']/1000

    def __str__ (self) :
        return "#{} from reservoir {}; data (waterGap={}[vcc={}], pH={}, conductivity={}, salinity={}, tds={})" \
            .format(self.packetNr, self.reservoir, self.waterGap, self.vcc,
                    self.pH, self.conductivity, self.salinity, self.tds)

    def save (self) :
        """
        Save this measurement to the database.
        """

        try:
            # This opens and closes the connections to the database.
            # Since writings occur only every 10 minutes it wouldn't be efficient to
            # let the connection open.
            db = MySQLdb.connect(
                host=config.db_host, db=config.db_name, user=config.db_user, passwd=config.db_password)
            cur = db.cursor()

            # get the reservoir height to be able to measure the water level
            sqlQuery = "SELECT heigth FROM main_reservoir WHERE res_id = {}".format(self.reservoir)
            cur.execute(sqlQuery)
            # self.waterGap is the height of the part of the reservoir
            # that's out of water. reservoir height minus that value will give the actual water level
            reservoirHeight = cur.fetchone()[0]
            waterLevel = reservoirHeight - self.waterGap

            sqlQuery = """
            INSERT INTO main_measurement (packetNr, waterLevel, pH, conductivity, reservoir_id, dateTime, salinity, tds)
            VALUES ({}, {}, {}, {}, {}, now(), {}, {})
            """.format(
                self.packetNr,
                waterLevel,
                self.pH,
                self.conductivity,
                self.reservoir,
                self.salinity,
                self.tds)
            cur.execute(sqlQuery)

            db.commit()
            db.close()
        except Exception as e:
            print('[Measurement#save] failed to save instance: {}'.format(e))
