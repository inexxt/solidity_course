// module.exports = {
//   // See <http://truffleframework.com/docs/advanced/configuration>
//   // to customize your Truffle configuration!
// };

module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*"
    },
  rinkeby: {
      host: "localhost", // Connect to geth on the specified
      port: 8545,
      from: "0x0afc1a8a3bf49f6a71c834b37841cec2f81731b1", // default address to use for any transaction Truffle makes during migrations
      network_id: 4,
      gas: 4612388 // Gas limit used for deploys
    }
}
};
