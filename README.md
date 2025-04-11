# yed_mulakat

## Servisler Nasıl Çalıştırılır
Aşağıdaki komut satırlarını sıra ile yazarak servisleri çalıştırabilirsiniz.

``` git clone https://github.com/SirmaXX/yed_mulakat.git```

cd yet_mulakat

sudo docker-compose build

sudo docker-compose up


## Backend tarafındai unit testler nasıl çalıştırabilirsiniz.
Aşağıdaki komut satırlarını sıra ile yazarak,backend servisi containerına erişerek unit testleri çalıştırabilirsiniz.


sudo docker exec -it backend /bin/bash




## Backend için endpointlere nasıl erişebilirsiniz
FastApi içerisinde swagger api ile otomatik oluşturulmuş dökümantasyona erişebilir ve endpointleri kendiniz manuel olarak test edebilirsiniz.
Bu linke tıkladığınız vakit otomatik oluşturulmuş döküman karşınıza çıkacaktır.
1. api dökümantasyonu http://localhost:8000/docs#/
2. jauger ui http://localhost:16686/search






