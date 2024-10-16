# Copyright(C) 2024 InfiniFlow, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
This example is to connect local infinity instance, create table, insert data, search the data
'''

import infinity

try:
    # open a local directory to store the data
    infinity_instance = infinity.connect("/var/infinity")

    # connect to server with 127.0.0.1
    # infinity_instance = infinity.connect(infinity.common.LOCAL_HOST)

    # 'default_db' is the default database
    db_instance = infinity_instance.get_database("default_db")

    # Drop my_table if it already exists
    db_instance.drop_table("my_table", infinity.common.ConflictType.Ignore)

    # Create a table named "my_table"
    table_instance = db_instance.create_table("my_table", {
        "num": {"type": "integer"},
        "body": {"type": "varchar"},
        "vec": {"type": "vector, 4, float"},
    })

    # Insert 3 rows of data into the 'my_table'
    table_instance.insert(
        [
            {
                "num": 1,
                "body": r"unnecessary and harmful",
                "vec": [1.0, 1.2, 0.8, 0.9],
            },
            {
                "num": 2,
                "body": r"Office for Harmful Blooms",
                "vec": [4.0, 4.2, 4.3, 4.5],
            },
            {
                "num": 3,
                "body": r"A Bloom filter is a space-efficient probabilistic data structure, conceived by Burton Howard Bloom in 1970, that is used to test whether an element is a member of a set.",
                "vec": [4.0, 4.2, 4.3, 4.2],
            },
        ]
    )

    # TODO: dense vector + sparse vector + full-text + structured data filter + tensor reranker
    result = table_instance.output(["num", "body"]).knn("vec", [3.0, 2.8, 2.7, 3.1], "float", "ip", 3).match("body",
                                                                                                             "blooms",
                                                                                                             "topn=1").fusion(
        "rrf").to_pl()
    print(result)
    infinity_instance.disconnect()

except Exception as e:
    print(str(e))
