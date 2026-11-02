# EstateVision AI: EDA findings

## 1. Distribution of property prices

Median: 253.87; mean: 254.59. Prices are in lakhs; sizes are in sq ft.

```text
index       Value
count 250000.0000
 mean    254.5869
  std    141.3499
  min     10.0000
  25%    132.5500
  50%    253.8700
  75%    376.8800
  max    500.0000
```

## 2. Distribution of property sizes

Median: 2,747.00; mean: 2,749.81. Prices are in lakhs; sizes are in sq ft.

```text
index       Value
count 250000.0000
 mean   2749.8132
  std   1300.6070
  min    500.0000
  25%   1623.0000
  50%   2747.0000
  75%   3874.0000
  max   5000.0000
```

## 3. Price per sq ft by property type

Table uses all records; box plot uses a reproducible sample of up to 5,000 records.

```text
    Property_Type  Price_per_SqFt
        Apartment        9244.510
Independent House        9304.860
            Villa        9190.265
```

## 4. Relationship between size and price

Correlation uses all records. The scatter plot samples up to 5,000 records.

```text
                         Statistic   Value
Pearson correlation: size vs price -0.0025
```

## 5. Outliers in price per sq ft and size

Outliers use the 1.5 × IQR rule. Flagging a record does not prove it is incorrect.

```text
       Feature  Lower bound  Upper bound  Outliers  Percentage
Price_per_SqFt  -11973.9888   32764.2212     19723      7.8892
  Size_in_SqFt   -1753.5000    7250.5000         0      0.0000
```

## 6. Average price per sq ft by state

These are descriptive associations in the supplied dataset, not causal effects.

```text
         State  Price_per_SqFt
     Karnataka      13252.2049
Andhra Pradesh      13201.5789
 Uttar Pradesh      13142.5196
    Tamil Nadu      13132.4208
     Telangana      13093.0989
       Gujarat      13091.1461
         Assam      13084.0216
   Maharashtra      13070.1338
Madhya Pradesh      13069.0292
       Haryana      13068.7409
```

## 7. Average property price by city

These are descriptive associations in the supplied dataset, not causal effects.

```text
      City  Price_in_Lakhs
 Bangalore        258.4566
     Surat        258.0805
     Kochi        257.4152
      Gaya        257.0534
 Mangalore        256.9209
  Dehradun        256.8901
    Mysore        256.8482
   Chennai        256.8302
 Hyderabad        256.5941
Coimbatore        256.5047
```

## 8. Median property age by locality

Localities are identified by state, city, and locality together. Age retains the dataset's original reference date. The chart shows the 25 highest median ages; the table includes all localities.

```text
      State      City     Locality  Age_of_Property
  Karnataka    Mysore Locality_444             34.5
Maharashtra    Mumbai Locality_349             34.0
  Karnataka    Mysore  Locality_70             34.0
  Telangana Hyderabad Locality_356             34.0
  Karnataka Bangalore  Locality_57             33.0
     Kerala     Kochi Locality_183             33.0
  Rajasthan    Jaipur Locality_249             33.0
  Karnataka Bangalore Locality_331             33.0
Maharashtra    Nagpur Locality_426             33.0
  Karnataka Mangalore Locality_344             33.0
```

## 9. BHK distribution across cities

These are descriptive associations in the supplied dataset, not causal effects.

```text
     City  BHK  Properties
Ahmedabad    1        1264
Ahmedabad    2        1267
Ahmedabad    3        1272
Ahmedabad    4        1258
Ahmedabad    5        1350
 Amritsar    1        1284
 Amritsar    2        1239
 Amritsar    3        1234
 Amritsar    4        1224
 Amritsar    5        1240
```

## 10. Five most expensive localities

Top five localities by mean asking price. Historical price trends cannot be calculated: no dated price history is supplied.

```text
      State      City     Locality  Price_in_Lakhs
Maharashtra    Mumbai Locality_350        492.4100
  Karnataka    Mysore  Locality_42        479.6300
Maharashtra      Pune Locality_129        476.0150
  Karnataka Mangalore  Locality_77        464.8833
    Gujarat     Surat Locality_138        442.8300
```

## 11. Correlation between numeric features

Pearson correlations. Price per sq ft is derived from price and size, so related correlations need careful interpretation.

```text
                  Price_in_Lakhs  Size_in_SqFt  Price_per_SqFt     BHK  Age_of_Property  Nearby_Schools  Nearby_Hospitals  Amenity_Count  Has_Parking  Has_Security
Price_in_Lakhs            1.0000       -0.0025          0.5558 -0.0010          -0.0027          0.0002           -0.0028         0.0010       0.0011        0.0038
Size_in_SqFt             -0.0025        1.0000         -0.6146 -0.0010          -0.0041          0.0020           -0.0017        -0.0023       0.0009        0.0008
Price_per_SqFt            0.5558       -0.6146          1.0000  0.0011           0.0013         -0.0001           -0.0001         0.0020      -0.0010        0.0003
BHK                      -0.0010       -0.0010          0.0011  1.0000          -0.0009         -0.0008            0.0012        -0.0023      -0.0023       -0.0009
Age_of_Property          -0.0027       -0.0041          0.0013 -0.0009           1.0000          0.0006            0.0027         0.0003       0.0006       -0.0000
Nearby_Schools            0.0002        0.0020         -0.0001 -0.0008           0.0006          1.0000           -0.0022        -0.0014      -0.0019       -0.0019
Nearby_Hospitals         -0.0028       -0.0017         -0.0001  0.0012           0.0027         -0.0022            1.0000        -0.0006      -0.0008        0.0011
Amenity_Count             0.0010       -0.0023          0.0020 -0.0023           0.0003         -0.0014           -0.0006         1.0000       0.0008        0.0036
Has_Parking               0.0011        0.0009         -0.0010 -0.0023           0.0006         -0.0019           -0.0008         0.0008       1.0000        0.0024
Has_Security              0.0038        0.0008          0.0003 -0.0009          -0.0000         -0.0019            0.0011         0.0036       0.0024        1.0000
```

## 12. Nearby schools and price per sq ft

Pearson correlation with price per sq ft: -0.0001. The chart shows group means, not a causal effect.

```text
 Nearby_Schools  Price_per_SqFt
              1      13061.4887
              2      13123.0244
              3      13073.0928
              4      12888.0810
              5      12993.0004
              6      13292.3610
              7      13041.2105
              8      12953.4339
              9      13102.9901
             10      13055.8043
```

## 13. Nearby hospitals and price per sq ft

Pearson correlation with price per sq ft: -0.0001. The chart shows group means, not a causal effect.

```text
 Nearby_Hospitals  Price_per_SqFt
                1      13019.8327
                2      13024.6771
                3      13233.6753
                4      12995.9897
                5      12917.0223
                6      13006.5572
                7      13256.9055
                8      13116.3154
                9      13084.2771
               10      12931.0265
```

## 14. Price by furnished status

These are descriptive associations in the supplied dataset, not causal effects.

```text
Furnished_Status  count     mean  median
       Furnished  83218 254.4455 253.555
  Semi-furnished  83374 254.3348 253.810
     Unfurnished  83408 254.9798 254.190
```

## 15. Price per sq ft by facing direction

These are descriptive associations in the supplied dataset, not causal effects.

```text
Facing  count       mean  median
  East  62269 13023.7009 9234.01
 North  62637 13024.8651 9219.23
 South  62337 13044.1104 9224.63
  West  62757 13140.0231 9307.59
```

## 16. Property counts by owner type

These are descriptive associations in the supplied dataset, not causal effects.

```text
Owner_Type  Properties
    Broker       83479
     Owner       83268
   Builder       83253
```

## 17. Property counts by availability

These are descriptive associations in the supplied dataset, not causal effects.

```text
Availability_Status  Properties
 Under_Construction      125035
      Ready_to_Move      124965
```

## 18. Parking and property price

These are descriptive associations in the supplied dataset, not causal effects.

```text
Parking_Space  count     mean  median
           No 125456 254.4294  253.37
          Yes 124544 254.7455  254.36
```

## 19. Amenities and price per sq ft

A property can appear in multiple amenity groups. These comparisons do not isolate the effect of an amenity.

```text
   Amenity  count       mean   median
 Clubhouse 150059 13069.6488 9242.130
    Garden 150177 13064.6287 9247.110
       Gym 149960 13097.4983 9268.695
Playground 149780 13048.8665 9260.115
      Pool 150096 13072.6874 9249.320
```

## 20. Transport access and price per sq ft

Transport groups are compared using price per sq ft. Real investment returns are not observed in this dataset.

```text
Public_Transport_Accessibility  count       mean  median
                          High  83705 13027.2422 9205.08
                           Low  83287 13085.5390 9265.33
                        Medium  83008 13062.2331 9269.31
```
