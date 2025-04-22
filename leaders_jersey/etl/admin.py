from django.contrib import admin, messages
from .models import ETLRun
from etl.extract.extract_stage import extract_stage_info, extract_stage_results
from etl.transform.transform_stage_info import transform_stage_info, transform_stage_results
from etl.load.load_stage_info import load_stage_info, load_stage_results
from etl.extract.extract_startlist import extract_startlist
from etl.transform.transform_startlist import transform_startlist
from etl.load.load_startlist import load_startlist
from django.template.loader import get_template

from etl.logging_config import logger  # ✅ in case you want to log debugging info
import pprint  # for optional pretty-print logging


class ETLRunAdmin(admin.ModelAdmin):
    list_display = ('race', 'stage')
    change_form_template = "admin/etl/etlrun/change_form.html"

    get_template('admin/etl/etlrun/change_form.html')

    def save_model(self, request, obj, form, change):
        if '_run_etl' in request.POST:
            race = obj.race
            year = race.year
            stage = obj.stage

            try:
                if obj.etl_type == 'startlist':
                    raw_startlist = extract_startlist(race.url_reference, year)

                    if raw_startlist is None or not isinstance(raw_startlist, dict):
                        raise ValueError("Startlist extract failed or returned unexpected format.")

                    logger.debug(f"Extracted startlist (first 500 chars): {pprint.pformat(raw_startlist)[:500]}")

                    transformed_startlist = transform_startlist(raw_startlist)

                    if transformed_startlist is None or transformed_startlist.empty:
                        raise ValueError("Startlist transform failed or returned empty DataFrame.")

                    load_startlist(transformed_startlist)

                elif obj.etl_type == 'stage_info':
                    raw_stage_data = extract_stage_info(race.url_reference, year)
                    transformed_data = transform_stage_info(raw_stage_data)
                    load_stage_info(transformed_data)

                elif obj.etl_type == 'stage_results':
                    if not stage:
                        raise ValueError("Stage must be selected for stage results ETL.")
                    raw_results = extract_stage_results(race.url_reference, year, stage.stage_number)
                    transformed_results = transform_stage_results(raw_results, race.url_reference, year, stage.stage_number)
                    load_stage_results(transformed_results)

                else:
                    raise ValueError("Invalid ETL type selected.")

                self.message_user(request, "✅ ETL process completed successfully.", level=messages.SUCCESS)

            except Exception as e:
                logger.error(f"ETL failed: {e}")
                self.message_user(request, f"❌ ETL failed: {e}", level=messages.ERROR)

            return  # Prevent saving the ETLRun

        super().save_model(request, obj, form, change)


admin.site.register(ETLRun, ETLRunAdmin)
