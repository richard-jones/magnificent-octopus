To deploy the application as a site under nginx using supervisor, take a copy of the file

    service.conf

Customise it to your needs, and place it in

    /etc/supervisor/conf.d
    
You can then restart supervisor with

    sudo supervisorctl reload

