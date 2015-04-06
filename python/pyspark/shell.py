#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
An interactive shell.

This file is designed to be launched as a PYTHONSTARTUP script.
"""

import sys
if sys.version_info[0] != 2:
    print("Error: Default Python used is Python%s" % sys.version_info.major)
    print("\tSet env variable PYSPARK_PYTHON to Python2 binary and re-run it.")
    sys.exit(1)


import atexit
import os
import platform
import pyspark
from pyspark.context import SparkContext
from pyspark.storagelevel import StorageLevel

# this is the equivalent of ADD_JARS
add_files = (os.environ.get("ADD_FILES").split(',')
             if os.environ.get("ADD_FILES") is not None else None)

if os.environ.get("SPARK_EXECUTOR_URI"):
    SparkContext.setSystemProperty("spark.executor.uri", os.environ["SPARK_EXECUTOR_URI"])

# We need a better way to figure out if we are within a notebook session.
# This is only a temporary solution that works for IPython 2.X and above.
def getNotebookName():
  try:
    import json
    import os
    import urllib2
    import IPython
    from IPython.lib import kernel
    connection_file_path = kernel.get_connection_file()
    connection_file = os.path.basename(connection_file_path)
    kernel_id = connection_file.split('-', 1)[1].split('.')[0]
    sessions = json.load(urllib2.urlopen('http://127.0.0.1:8888/api/sessions'))
    for sess in sessions:
        if sess['kernel']['id'] == kernel_id:
            notebook_name = sess['notebook']['name']
            break
  except Exception as ex:
    notebook_name = "PySparkShell"

  return notebook_name

sc = SparkContext(appName=getNotebookName(), pyFiles=add_files)
atexit.register(lambda: sc.stop())

print("""Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version %s
      /_/
""" % sc.version)
print("Using Python version %s (%s, %s)" % (
    platform.python_version(),
    platform.python_build()[0],
    platform.python_build()[1]))
print("SparkContext available as sc.")

if add_files is not None:
    print("Adding files: [%s]" % ", ".join(add_files))

# The ./bin/pyspark script stores the old PYTHONSTARTUP value in OLD_PYTHONSTARTUP,
# which allows us to execute the user's PYTHONSTARTUP file:
_pythonstartup = os.environ.get('OLD_PYTHONSTARTUP')
if _pythonstartup and os.path.isfile(_pythonstartup):
    execfile(_pythonstartup)
