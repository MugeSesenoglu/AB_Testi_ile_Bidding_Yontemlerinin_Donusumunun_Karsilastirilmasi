###############################################################
# AB Testi ile Bidding Yöntemlerinin Dönüşümünün Karşılaştırılması
###############################################################

#Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif olarak yeni bir teklif türü olan
#"average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com, bu yeni özelliği test
#etmeye karar verdi ve average bidding'inmaximumbidding'den daha fazla dönüşüm getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.
#A/B testi 1 aydır devam ediyor ve bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.
#Bombabomba.com için nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchase metriğine odaklanılmalıdır.

########################################
#  Veri Seti Hikayesi
########################################

#Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları reklam sayıları gibi bilgilerin yanı sıra
#buradan gelen kazanç bilgileri yer almaktadır. Kontrol ve Test grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleri
#ab_testing.xlsx excel’inin ayrı sayfalarında yer almaktadır. Kontrol grubuna Maximum Bidding, test grubuna Average
#Bidding uygulanmıştır.

# Değişkenler
#Impression : Reklam görüntüleme sayısı
#Click : Görüntülenen reklama tıklama sayısı
#Purchase : Tıklanan reklamlar sonrası satın alınan ürün sayısı
#Earning : Satın alınan ürünler sonrası elde edilen kazanç

###############################################################
# PROJE Görevleri
###############################################################

##########################################################################################################
# GÖREV 1: Veriyi Hazırlama ve Analiz Etme
##########################################################################################################

import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#pip install statsmodels
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

#Adım 1: ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı
#değişkenlere atayınız.

df_control = pd.read_excel('datasets/ab_testing.xlsx',sheet_name='Control Group')
df_test = pd.read_excel('datasets/ab_testing.xlsx',sheet_name='Test Group')

#Adım 2: Kontrol ve test grubu verilerini analiz ediniz.

df_control.head()
df_test.head()
df_control.describe().T
df_test.describe().T

#Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

df_control.columns = [i + "_control" for i in df_control.columns]
df_control.head()
df_test.columns = [i + "_test" for i in df_test.columns]
df_test.head()
df_final = pd.concat([df_control,df_test],axis=1)
df_final.head()

##################################################################################
# GÖREV 2: A/B Testinin Hipotezinin Tanımlanması
##################################################################################

#Adım 1: Hipotezi tanımlayınız.
#H0 : M1 = M2 Average bidding ve Max bidding'in satın alma ortalamaları arasında istatistiki olarak anlamlı bir fark yoktur.
#H1 : M1!= M2 Average bidding ve Max bidding'in satın alma ortalamaları arasında istatistiki olarak anlamlı bir fark vardır.

#Adım 2: Kontrol ve test grubu için purchase (kazanç) ortalamalarını analiz ediniz.

df_final[["Purchase_control","Purchase_test"]].mean()

#ilk bakışta matematiksel olarak yeni sistem fark yaratmış gözüküyor.

##################################################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
##################################################################################

#Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.
#Bunlar Normallik Varsayımı ve Varyans Homojenliğidir. Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni
#üzerinden ayrı ayrı test ediniz.

#Normallik Varsayımı :
#H0: Normal dağılım varsayımı sağlanmaktadır.
#H1: Normal dağılım varsayımı sağlanmamaktadır.

#p < 0.05 H0 RED , p > 0.05 H0 REDDEDİLEMEZ

#Test sonucuna göre normallik varsayımı kontrol ve test grupları için sağlanıyor mu ? Elde edilen p-value değerlerini yorumlayınız.

test_stat, pvalue = shapiro(df_final["Purchase_control"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

test_stat, pvalue = shapiro(df_final["Purchase_test"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

#Karşılaştırdığımız iki grubunda p_value değeri 0.05'ten büyük.Yani burada iki grup içinde diyebiliriz ki p-value değeri 0.05'ten
#büyük olduğu için H0 hipoteziREDDEDİLEMEZ.Normal dağılım varsayımı sağlanmıştır.

#Varyans Homojenliği :
#H0: Varyanslar homojendir.
#H1: Varyanslar homojen Değildir.

#p < 0.05 H0 RED , p > 0.05 H0 REDDEDİLEMEZ

#Kontrol ve test grubu için varyans homojenliğinin sağlanıp sağlanmadığını Purchase değişkeni üzerinden test ediniz.
#Test sonucuna göre normallik varsayımı sağlanıyor mu? Elde edilen p-value değerlerini yorumlayınız.

test_stat, pvalue = levene(df_final["Purchase_control"],
                           df_final["Purchase_test"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

#Karşılaştırdığımız iki grubunda p_value değeri 0.05'ten büyük.Yani burada iki grup içinde diyebiliriz ki p-value değeri 0.05'ten
#büyük olduğu için H0 hipoteziREDDEDİLEMEZ.Varyanslar homojendir.

#Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz.

#Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma ortalamaları arasında istatistiki
#olarak anlamlı bir fark olup olmadığını yorumlayınız.

#İki varsayım hipotezleri de reddedilemedi yani varsayımlar sağlandı.
#Bu yüzden bizde parametrik T testimizi uygulayıp sonucumuza bakabiliriz.

test_stat, pvalue = ttest_ind(df_final["Purchase_control"],
                              df_final["Purchase_test"],
                              equal_var=True)

print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# p değeri 0,05'ten büyük olduğundan H0 Reddedilmez.Dolasıyla Average bidding ve Max bidding'in satın alma ortalamaları arasında
#istatistiksel olarak anlamlı bir fark yoktur.

##################################################################################
# GÖREV 4: Sonuçların Analizi
##################################################################################

#Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.

#Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.

