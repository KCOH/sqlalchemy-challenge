{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "27955ced",
   "metadata": {},
   "outputs": [],
   "source": [
    "# import dependency\n",
    "import sqlalchemy\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func, distinct\n",
    "import numpy as np\n",
    "\n",
    "from flask import Flask, jsonify"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "7b3914c4",
   "metadata": {},
   "outputs": [],
   "source": [
    "#################################################\n",
    "# Database Setup\n",
    "#################################################"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "d10cd4b3",
   "metadata": {},
   "outputs": [],
   "source": [
    "engine = create_engine(\"sqlite:///Resources/hawaii.sqlite\")\n",
    "Base = automap_base()\n",
    "Base.prepare(engine, reflect=True)\n",
    "climate = Base.classes.measurement"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "00b43c46",
   "metadata": {},
   "outputs": [],
   "source": [
    "#################################################\n",
    "# Flask Setup\n",
    "#################################################\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "0f12627b",
   "metadata": {},
   "outputs": [],
   "source": [
    "app = Flask(__name__)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "57a3f14f",
   "metadata": {},
   "outputs": [],
   "source": [
    "#################################################\n",
    "# Flask Routes\n",
    "#################################################"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "4b55b2c0",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/\")\n",
    "def home():\n",
    "    return (\n",
    "        f\"Welcome to the Climate API!<br/>\"\n",
    "        f\"Available Routes:<br/>\"\n",
    "        f\"/api/v1.0/precipitation<br/>\"\n",
    "        f\"/api/v1.0/stations<br/>\"\n",
    "        f\"/api/v1.0/tobs<br/>\"\n",
    "        f\"/api/v1.0/<start><br/>\"\n",
    "        f\"/api/v1.0/<start>/<end><br/>\" \n",
    "    )"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "c5c3b8ce",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/precipitation\")\n",
    "def precipitation():\n",
    "    session = Session(engine)\n",
    "    results = session.query(climate.date, climate.prcp).all()\n",
    "    session.close()\n",
    "    date = []\n",
    "    prcp = []\n",
    "    for ddate, dprcp in results:\n",
    "        date.append(ddate)\n",
    "        prcp.append(dprcp)\n",
    "    precipitation = dict(zip(date, prcp))    \n",
    "    \n",
    "    return jsonify(precipitation)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "6efcd4c2",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/stations\")\n",
    "def stations():\n",
    "    session = Session(engine)\n",
    "    results = session.query(distinct(climate.station)).all()\n",
    "    station = list(np.ravel(results))\n",
    "    \n",
    "    return jsonify(station)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "33b773f9",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/tobs\")\n",
    "def temperature():\n",
    "    session = Session(engine)\n",
    "    recent_date = session.query(climate.date).\\\n",
    "        order_by(climate.date.desc()).first()[0]\n",
    "    \n",
    "    year = str(recent_date).split(\"-\")[0]\n",
    "    last_year = str(int(year)-1)\n",
    "    \n",
    "    active_station = session.query(climate.station, func.count(climate.station)).\\\n",
    "        filter(func.strftime(\"%Y\", climate.date) == last_year).\\\n",
    "        group_by(climate.station).\\\n",
    "        order_by(func.count(climate.station).desc()).first()[0]\n",
    "    \n",
    "    temperature = session.query(climate.tobs).\\\n",
    "        filter(func.strftime(\"%Y\", climate.date) == last_year).\\\n",
    "        filter(climate.station==active_station).all()\n",
    "    temp = list(np.ravel(temperature))        \n",
    "\n",
    "    return jsonify(temp)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "dda5ba1e",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>\")\n",
    "def start_date(start):\n",
    "    session = Session(engine)\n",
    "    temp = session.query(func.min(climate.tobs),\n",
    "        func.max(climate.tobs), \n",
    "        func.avg(climate.tobs)).\\\n",
    "        filter(climate.date>=start).all()\n",
    "    \n",
    "    temperature = list(np.ravel(temp))\n",
    "    name = ['TMIN', 'TMAX', 'TAVG']\n",
    "    stats = dict(zip(name, temperature))\n",
    "    return jsonify(stats)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "fc306255",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>/<end>\")\n",
    "def start_end_date(start, end):\n",
    "    session = Session(engine)\n",
    "    temp = session.query(func.min(climate.tobs),\n",
    "        func.max(climate.tobs), \n",
    "        func.avg(climate.tobs)).\\\n",
    "        filter(climate.date.between(start, end)).all()\n",
    "    \n",
    "    temperature = list(np.ravel(temp))\n",
    "    name = ['TMIN', 'TMAX', 'TAVG']\n",
    "    stats = dict(zip(name, temperature))\n",
    "    \n",
    "    return jsonify(stats) "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "2053c3eb",
   "metadata": {
    "collapsed": true
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app \"__main__\" (lazy loading)\n",
      " * Environment: production\n",
      "   WARNING: This is a development server. Do not use it in a production deployment.\n",
      "   Use a production WSGI server instead.\n",
      " * Debug mode: on\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " * Restarting with windowsapi reloader\n"
     ]
    },
    {
     "ename": "SystemExit",
     "evalue": "1",
     "output_type": "error",
     "traceback": [
      "An exception has occurred, use %tb to see the full traceback.\n",
      "\u001b[1;31mSystemExit\u001b[0m\u001b[1;31m:\u001b[0m 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\ohkyu\\anaconda3\\lib\\site-packages\\IPython\\core\\interactiveshell.py:3445: UserWarning: To exit: use 'exit', 'quit', or Ctrl-D.\n",
      "  warn(\"To exit: use 'exit', 'quit', or Ctrl-D.\", stacklevel=1)\n"
     ]
    }
   ],
   "source": [
    "if __name__ == \"__main__\":\n",
    "    app.run(debug=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "442a8089",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
