import time

from numpy import dtype
import pandas as pd
import pytest
from infinity_cluster import InfinityCluster
from infinity.common import ConflictType
from infinity.common import InfinityException
from infinity.errors import ErrorCode


class TestDelete:
    def test_delete(self, cluster: InfinityCluster):
        try:
            cluster.add_node("node1", "conf/leader.toml")
            cluster.add_node("node2", "conf/follower.toml")

            print("init nodes")
            cluster.set_leader("node1")
            cluster.set_follower("node2")
            time.sleep(1)

            infinity1 = cluster.client("node1")
            infinity2 = cluster.client("node2")

            db_obj = infinity1.get_database("default_db")

            db_obj.drop_table(table_name="test_delete", conflict_type=ConflictType.Ignore)
            res = db_obj.create_table(
                "test_delete",
                {"c1": {"type": "int", "constraints": ["primary key", "not null"]},
                "c2": {"type": "int"}, "c3": {"type": "int"}}, ConflictType.Error)

            table_obj = db_obj.get_table("test_delete")

            res = table_obj.insert(
                [{"c1": 1, "c2": 10, "c3": 100}, {"c1": 2, "c2": 20, "c3": 200}, {"c1": 3, "c2": 30, "c3": 300},
                {"c1": 4, "c2": 40, "c3": 400}])
            assert res.error_code == ErrorCode.OK

            res = table_obj.delete("c1 = 1")
            assert res.error_code == ErrorCode.OK

            res = table_obj.output(["*"]).to_df()
            pd.testing.assert_frame_equal(res, pd.DataFrame({'c1': (2, 3, 4), 'c2': (20, 30, 40), 'c3': (200, 300, 400)})
                                        .astype({'c1': dtype('int32'), 'c2': dtype('int32'), 'c3': dtype('int32')}))

            time.sleep(1)
            db_obj_2 = infinity2.get_database("default_db")
            table_obj_2 = db_obj_2.get_table("test_delete")
            res = table_obj_2.output(["*"]).to_df()
            pd.testing.assert_frame_equal(res, pd.DataFrame({'c1': (2, 3, 4), 'c2': (20, 30, 40), 'c3': (200, 300, 400)})
                                        .astype({'c1': dtype('int32'), 'c2': dtype('int32'), 'c3': dtype('int32')}))            

            res = table_obj.delete()
            assert res.error_code == ErrorCode.OK

            res = table_obj.output(["*"]).to_df()
            pd.testing.assert_frame_equal(res, pd.DataFrame({'c1': (), 'c2': (), 'c3': ()})
                                        .astype({'c1': dtype('int32'), 'c2': dtype('int32'), 'c3': dtype('int32')}))

            res = table_obj_2.output(["*"]).to_df()
            pd.testing.assert_frame_equal(res, pd.DataFrame({'c1': (), 'c2': (), 'c3': ()})
                                        .astype({'c1': dtype('int32'), 'c2': dtype('int32'), 'c3': dtype('int32')}))

            res = db_obj.drop_table("test_delete")
            assert res.error_code == ErrorCode.OK


        except Exception as e:
            print(e)
            cluster.clear()
            raise
        else:
            cluster.clear()

    def test_delete_on_follower(self, cluster: InfinityCluster):
        try:
            cluster.add_node("node1", "conf/leader.toml")
            cluster.add_node("node2", "conf/follower.toml")

            print("init nodes")
            cluster.set_leader("node1")
            cluster.set_follower("node2")
            time.sleep(1)

            infinity1 = cluster.client("node1")
            infinity2 = cluster.client("node2")

            db_obj = infinity1.get_database("default_db")

            db_obj.drop_table(table_name="test_delete", conflict_type=ConflictType.Ignore)
            res = db_obj.create_table(
                "test_delete",
                {"c1": {"type": "int", "constraints": ["primary key", "not null"]},
                "c2": {"type": "int"}, "c3": {"type": "int"}}, ConflictType.Error)

            table_obj = db_obj.get_table("test_delete")

            res = table_obj.insert(
                [{"c1": 1, "c2": 10, "c3": 100}, {"c1": 2, "c2": 20, "c3": 200}, {"c1": 3, "c2": 30, "c3": 300},
                {"c1": 4, "c2": 40, "c3": 400}])
            assert res.error_code == ErrorCode.OK

            time.sleep(1)
            db_obj_2 = infinity2.get_database("default_db")
            table_obj_2 = db_obj_2.get_table("test_delete")           

            try:
                table_obj_2.delete("c1 = 1")
            except InfinityException as e:
                print(e)
                assert(e.error_code == 8007)

            res = table_obj.output(["*"]).to_df()
            pd.testing.assert_frame_equal(res, pd.DataFrame({'c1': (1, 2, 3, 4), 'c2': (10, 20, 30, 40), 'c3': (100, 200, 300, 400)})
                                        .astype({'c1': dtype('int32'), 'c2': dtype('int32'), 'c3': dtype('int32')}))

            res = table_obj_2.output(["*"]).to_df()
            pd.testing.assert_frame_equal(res, pd.DataFrame({'c1': (1, 2, 3, 4), 'c2': (10, 20, 30, 40), 'c3': (100, 200, 300, 400)})
                                        .astype({'c1': dtype('int32'), 'c2': dtype('int32'), 'c3': dtype('int32')}))

            res = db_obj.drop_table("test_delete")
            assert res.error_code == ErrorCode.OK


        except Exception as e:
            print(e)
            cluster.clear()
            raise
        else:
            cluster.clear()