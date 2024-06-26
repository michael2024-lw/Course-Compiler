﻿// This is a personal academic project. Dear PVS-Studio, please check it.
// PVS-Studio Static Code Analyzer for C, C++, C#, and Java: http://www.viva64.com
using Compilation.Parser.IOstructs;

namespace Compilation.Parser {
    class Program {
        static void Main(string[] args) {
            MicroServerAPI.MicroService mserv = new("http://localhost:8080/5-semestr/compiler/get-job", "http://localhost:8080/5-semestr/compiler/post-job", true);

            while (true) {
                Input session = mserv.GetJob<Input>("Compilation.Parser", out MicroServerAPI.ResponseAddress address);

                Processor processor = new(session);
                Output output = processor.Run();

                mserv.PostFinalResult<Output>("Compilation.Parser.Output", address, output);
            }
        }
    }
}
