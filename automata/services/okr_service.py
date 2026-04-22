# MIT License
#
# Copyright (c) 2026 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# SPDX-License-Identifier: MIT

from typing import List, Optional

from automata.core.models import KeyResult, Okr, db


class OKRService:
    @staticmethod
    def get_all_okrs(
        goal_id: Optional[int] = None, quarter: Optional[str] = None
    ) -> List[Okr]:
        query = Okr.select()
        if goal_id:
            query = query.where(Okr.goal == goal_id)
        if quarter:
            query = query.where(Okr.quarter == quarter)
        return list(query.order_by(Okr.created_at.desc()))

    @staticmethod
    def get_okr_by_id(okr_id: int) -> Optional[Okr]:
        return Okr.get_or_none(Okr.id == okr_id)

    @staticmethod
    def get_okrs_by_quarter(quarter: str) -> List[Okr]:
        return list(Okr.select().where(Okr.quarter == quarter))

    @staticmethod
    def create_okr(**kwargs) -> Okr:
        with db.atomic():
            return Okr.create(**kwargs)

    @staticmethod
    def update_okr(okr_id: int, **kwargs) -> Optional[Okr]:
        okr = Okr.get_or_none(Okr.id == okr_id)
        if okr:
            for key, value in kwargs.items():
                if hasattr(okr, key):
                    setattr(okr, key, value)
            okr.save()
        return okr

    @staticmethod
    def delete_okr(okr_id: int) -> bool:
        okr = Okr.get_or_none(Okr.id == okr_id)
        if okr:
            okr.delete_instance(recursive=True)
            return True
        return False


class KeyResultService:
    @staticmethod
    def get_key_results(okr_id: int) -> List[KeyResult]:
        return list(KeyResult.select().where(KeyResult.okr == okr_id))

    @staticmethod
    def get_key_result_by_id(kr_id: int) -> Optional[KeyResult]:
        return KeyResult.get_or_none(KeyResult.id == kr_id)

    @staticmethod
    def create_key_result(**kwargs) -> KeyResult:
        with db.atomic():
            return KeyResult.create(**kwargs)

    @staticmethod
    def update_key_result(kr_id: int, **kwargs) -> Optional[KeyResult]:
        kr = KeyResult.get_or_none(KeyResult.id == kr_id)
        if kr:
            for key, value in kwargs.items():
                if hasattr(kr, key):
                    setattr(kr, key, value)
            kr.save()
        return kr

    @staticmethod
    def delete_key_result(kr_id: int) -> bool:
        kr = KeyResult.get_or_none(KeyResult.id == kr_id)
        if kr:
            kr.delete_instance()
            return True
        return False

    @staticmethod
    def update_progress(kr_id: int, current: float) -> Optional[KeyResult]:
        kr = KeyResult.get_or_none(KeyResult.id == kr_id)
        if kr:
            kr.current = current
            kr.save()
        return kr


okr_service = OKRService()
key_result_service = KeyResultService()
