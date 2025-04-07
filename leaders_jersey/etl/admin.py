from django.contrib import admin, messages
from .models import ETLRun
from etl.extract.extract_stage import extract_stage_info, extract_stage_results
from etl.transform.transform_stage_info import transform_stage_info, transform_stage_results
from etl.load.load_stage_info import load_stage_info, load_stage_results
from etl.extract.extract_startlist import extract_startlist
from etl.transform.transform_startlist import transform_startlist
from etl.load.load_startlist import load_startlist
from django.template.loader import get_template

class ETLRunAdmin(admin.ModelAdmin):
    list_display = ('race', 'stage')
    change_form_template = "admin/etl/etlrun/change_form.html"

    get_template('admin/etl/etlrun/change_form.html')

    def save_model(self, request, obj, form, change):
        if '_run_etl' in request.POST:
            race = obj.race
            year = race.year
            stage = obj.stage  # not always needed, but prepare

            try:
                if obj.etl_type == 'startlist':
                    # 🆕 Startlist ETL
                    raw_startlist = extract_startlist(race.url_reference, year)
                    transformed_startlist = transform_startlist(raw_startlist)
                    load_startlist(transformed_startlist)

                elif obj.etl_type == 'stage_info':
                    # Stage Info ETL
                    raw_stage_data = extract_stage_info(race.url_reference, year)
                    transformed_data = transform_stage_info(raw_stage_data)
                    load_stage_info(transformed_data)

                elif obj.etl_type == 'stage_results':
                    # Stage Results ETL
                    if not stage:
                        raise ValueError("Stage must be selected for stage results ETL.")

                    raw_results = extract_stage_results(race.url_reference, year, stage.stage_number)
                    transformed_results = transform_stage_results(raw_results, race.url_reference, year, stage.stage_number)
                    load_stage_results(transformed_results)

                else:
                    raise ValueError("Invalid ETL type selected.")

                self.message_user(request, "✅ ETL process completed successfully.", level=messages.SUCCESS)

            except Exception as e:
                self.message_user(request, f"❌ ETL failed: {e}", level=messages.ERROR)

            return  # prevent save

        super().save_model(request, obj, form, change)

admin.site.register(ETLRun, ETLRunAdmin)
