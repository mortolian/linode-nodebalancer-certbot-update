```bash
docker run -it --rm --name certbot \
            -v "./.docker/certbot/etc/letsencrypt:/etc/letsencrypt" \
            -v "./.docker/certbot/var/lib/letsencrypt:/var/lib/letsencrypt" \
            certbot/certbot renew
```

- https://stackoverflow.com/questions/37458287/how-to-run-a-cron-job-inside-a-docker-container
- https://devtron.ai/blog/running-cronjob-inside-docker-container/

- https://stackoverflow.com/questions/37458287/how-to-run-a-cron-job-inside-a-docker-container

- https://betterstack.com/community/questions/how-to-run-cron-jobs-inside-docker-container/

1. Write the action to take to a temporary file on the host. This is how you will know what other commmands will have to do.
2. So let the hook script write a file with a renewal request... like the messaging service with flat files. (it can check a directory for files to execute.)
3. A new image based on the certbot:cloudflare image can then have the cron installed, with the same folders mounted.
4. This will run the cron from the cron file we will mount to this image.
5. The cert renewal will be checked once a day.

6. You can use docker compose to run two services wich run crons.
7. The one service will check whether certs were renewed, and the other one will install a cert if it finds the "deploy" file on the directory structure.
8. in both cases the services are based on the already available images... one built on top of PYTHON and the other on CERTBOT.

9. You will need a start or installation MAKE command of sorts.


---

Limit the automated renewals to linux, where Docker and CRON can run.

