from datetime import date

from stats import utils



class TestWeekRange(object):

    @pytest.mark.parametrize("ref_date", [
        (date(2017, 2, 14), date(2017, 2, 12), date(2017, 2, 18)),
        (date(2017, 2, 1), date(2017, 1, 29), date(2017, 2, 4)))])
    def test_accuracy_for_day_within_week(self, ref_date):
        pass
    
    @pytest.mark.parametrize("ref_date", [
        (date(2017, 2, 13), 0, date(2017, 2, 12), date(2017, 2, 19)),
        (date(2017, 2, 19), 0, date(2017, 2, 12), date(2017, 2, 19)),
        (date(2017, 2, 12), 6, date(2017, 2, 12), date(2017, 2, 18)),
        (date(2017, 2, 18), 6, date(2017, 2, 12), date(2017, 2, 18))])
    def test_accuracy_for_day_on_week_edge(self, ref_date):
        # note: edge of week is either first day or last day of week
        pass
    
    @pytest.mark.parametrize("ref_date, firstweekday", [
        (date(2017, 2, 14), 6, date(2017, 2, 12), date(2017, 2, 18)),
        (date(2017, 2, 14), 0, date(2017, 2, 13), date(2017, 2, 19))])
    def test_firstweekday_considered_for_range(self, ref_date, firstweekday):
        pass
    
    @pytest.mark.parametrize("ref_date, firstweekday", [
        (date.today(), 1), (date.today(), 2), (date.today(), 3), 
        (date.today(), 4), (date.today(), 5), (date.today(), 7),
        (date.today(), -1)])
    def test_range_fails_for_firstweekday_not_equal_0_or_6(self, ref_date, firstweekday):
        pass


class TestFortNightRange(object):
    def test_accuracy_for_day_within_week(self, ref_date):
        pass