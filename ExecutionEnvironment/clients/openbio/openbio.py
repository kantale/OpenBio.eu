

def run_workflow(request, **kwargs):
    ############## HIGHLY EXPERIMENTAL ###############################

# ...or continue with "experimental" code.
    run_url = urllib.parse.urljoin(url + '/', 'run') # https://stackoverflow.com/questions/8223939/how-to-join-absolute-and-relative-urls

    data_to_submit = {
        'type': 'workflow',
        'name': name,
        'edit': edit,
        'callback': callback_url(request),
        'workflow_id': nice_id,
        'input_parameters' : workflow_options,
    }

    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

    #print ('run_url:', run_url)
    #print ('callback:', data_to_submit['callback'])

    '''


    '''

    '''
curl --header "Content-Type: application/json" \
  --request GET \
  http://139.91.190.239:5000/cfa52d9df5a24345d9f740395e4e69e4/check/id/test



[{"dag_id": "mitsos", "dag_run_url": "/admin/airflow/graph?dag_id=mitsos&execution_date=2020-02-28+13%3A16%3A42%2B00%3A00", "execution_date": "2020-02-28T13:16:42+00:00", "id": 2, "run_id": "manual__2020-02-28T13:16:42+00:00", "start_date": "2020-02-28T13:16:42.710933+00:00", "state": "success"}, {"dag_id": "mitsos", "dag_run_url": "/admin/airflow/graph?dag_id=mitsos&execution_date=2020-02-28+13%3A20%3A44%2B00%3A00", "execution_date": "2020-02-28T13:20:44+00:00", "id": 3, "run_id": "manual__2020-02-28T13:20:44+00:00", "start_date": "2020-02-28T13:20:44.423814+00:00", "state": "success"}, {"dag_id": "mitsos", "dag_run_url": "/admin/airflow/graph?dag_id=mitsos&execution_date=2020-02-28+13%3A24%3A02%2B00%3A00", "execution_date": "2020-02-28T13:24:02+00:00", "id": 4, "run_id": "manual__2020-02-28T13:24:02+00:00", "start_date": "2020-02-28T13:24:02.486982+00:00", "state": "success"}]

    '''

    # !!!HIGLY EXPERIMENTAL!!!
    try:
        print('RUNNING WITH CLIENT AT URL:', run_url, 'HEADERS:', headers, 'DATA:', data_to_submit)
        r = requests.post(run_url, headers=headers, data=simplejson.dumps(data_to_submit))
    except requests.exceptions.ConnectionError as e:
        return fail('Could not establish a connection with client')

    if not r.ok:
        #r.raise_for_status()
        return fail('Could not send to URL: {} . Error code: {}'.format(run_url, r.status_code))
    try:
        data_from_client = r.json()
    except Exception as e: # Ideally we should do here: except json.decoder.JSONDecodeError as e: but we would have to import json with simp[lejson..]
        return fail('Could not parse JSON data from Execution Client.')

    #print ('RUN_URL:')
    #print (data_from_client)

    # Check data_from_client. We expect to find an externally triggered True in data_from_client['status']['message']
    if not 'status' in data_from_client:
        return fail('Client does not contains status info')

    if not 'message' in data_from_client['status']:
        return fail("Client's status does not contain any message")

    if not 'externally triggered: True' in data_from_client['status']['message']:
        return fail("Client failed to trigger DAG: {}".format(data_from_client['status']['message']))

    if not 'executor_url' in data_from_client:
        return fail("Could not get workflow monitoring URL..")
    visualization_url = g['create_client_airflow_url'](data_from_client['executor_url'], nice_id)

    if not 'monitor_url' in data_from_client:
        return fail('Could not get monitoring URL..')
    monitor_url = data_from_client['monitor_url']


    # All seem to be ok. Create a report
    report = Report(
        obc_user=obc_user,
        workflow = workflow,
        nice_id = nice_id,
        client=client,
        visualization_url=visualization_url,
        monitor_url = monitor_url,
        client_status='SUBMITTED')
    report.save()

    # Let's not create a report token for now.
    ret = {
        'nice_id': nice_id,
    }

    return success(ret)


