{{- define "rebellis.name" -}}rebellis{{- end -}}
{{- define "rebellis.fullname" -}}{{- printf "%s" .Release.Name -}}{{- end -}}
{{- define "rebellis.chart" -}}{{- printf "%s-%s" .Chart.Name .Chart.Version -}}{{- end -}}
