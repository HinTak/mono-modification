$ rpm -q --requires mono-core | grep Cecil
mono(Mono.Cecil) = 0.10.0.0
mono(Mono.Cecil) = 0.10.3.0

$ rpm -q --provides mono-core | grep Cecil
mono(Mono.Cecil) = 0.10.3.0
mono(Mono.Cecil) = 0.9.5.0

$ rpm -q --provides mono-cecil
mono(Mono.Cecil) = 0.10.4.0
mono(Mono.Cecil.Mdb) = 0.10.4.0
mono(Mono.Cecil.Pdb) = 0.10.4.0
mono(Mono.Cecil.Rocks) = 0.10.4.0
mono-cecil = 0.10.4-7.fc37
mono-cecil(x86-64) = 0.10.4-7.fc37
