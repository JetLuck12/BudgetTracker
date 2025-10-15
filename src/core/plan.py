import json
import os


class PlanParser:
    @staticmethod
    def parse(plan_file):
        if not os.path.exists(plan_file):
            return []
        with open(plan_file, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_plan(plan, plan_file):
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan.to_json(), f, ensure_ascii=False, indent=2)


class Plan:
    def __init__(self, plan_json):
        self.plan_json = plan_json
        self.plan = dict()
        for p in plan_json:
            cat = p["category"]
            self.plan[cat] = p["plan_expense"]

    def to_json(self):
        return self.plan_json
