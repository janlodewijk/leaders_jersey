from django.contrib import admin, messages
from .models import ETLRun
from etl.extract.extract_stage import extract_stage_info, extract_stage_results
from etl.transform.transform_stage_info import transform_stage_info, transform_stage_results
from etl.load.load_stage_info import load_stage_info, load_stage_results
from django.template.loader import get_template

class ETLRunAdmin(admin.ModelAdmin):
    list_display = ('race', 'stage')
    change_form_template = 'admin/etlrun_change_form.html'

    get_template('admin/etl/etlrun/change_form.html')

    def save_model(self, request, obj, form, change):
        if '_run_etl' in request.POST:
            race = obj.race
            year = race.year
            stage = obj.stage

            try:
                raw_stage_data = extract_stage_info(race.url_reference, year)
                transformed_data = transform_stage_info(raw_stage_data, race.url_reference, year)
                load_stage_info(transformed_data)

                if stage:
                    raw_results = extract_stage_results(race.url_reference, year, stage.stage_number)
                    transformed_results = transform_stage_results(raw_results, race.url_reference, year, stage.stage_number)
                    load_stage_results(transformed_results)

                self.message_user(request, "✅ ETL process completed successfully.", level=messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"❌ ETL failed: {e}", level=messages.ERROR)

            return  # Skip saving the model

        super().save_model(request, obj, form, change)


admin.site.register(ETLRun, ETLRunAdmin)
